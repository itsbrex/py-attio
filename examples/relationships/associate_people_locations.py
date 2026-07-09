#!/usr/bin/env python3

"""
Associate People <> Locations based on existing Company <> People and Company <> Locations

This script:
- Efficiently processes only companies with recently created/updated people
- Uses date-based filtering to avoid reprocessing unchanged data
- Updates each related Person to include the Company's Locations in a chosen
  People->Locations relationship attribute

Usage:
  export ATTIO_API_KEY=...  # or pass --api-key
  python examples/relationships/associate_people_locations.py \
    --company-object companies \
    --company-people-attr people \
    --company-locations-attr locations \
    --people-object people \
    --location-object locations \
    --people-locations-attr locations \
    --page-size 100 \
    --state-file .state.json \
    --dry-run

How it works:
1. Loads timestamp of last successful run from state file
2. Filters people created/updated since last run using Attio's date filters
3. Finds companies associated with those recently modified people (single
   checkpointed scan; an interrupted scan resumes where it left off)
4. Only processes those specific companies (much more efficient!)
5. Saves new timestamp only after a fully successful, non-dry-run completion
6. Appends every attempted update (success, dry-run, or failure) to an
   append-only JSONL audit log so the paper trail of who is associated to
   which locations is never lost

Reliability guarantees:
- State/checkpoint files are written atomically (crash-safe)
- Dry runs never advance the incremental window
- If any update fails, the timestamp is NOT advanced; the next run retries
  the same window. Retries are idempotent (superset check skips done work).
"""

import argparse
import os
import sys
import time

# Ensure we can import the local package when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import py_attio  # noqa: E402
from py_attio.relationships import (  # noqa: E402
    collect_target_companies,
    get_recently_modified_people,
    sync_person_locations,
)
from py_attio.utils import (  # noqa: E402
    checkpoint_path_for,
    load_env_file,
    load_json_state,
    save_json_state,
    utc_now_iso,
)

# Load .env from repo root (already-exported env vars win)
load_env_file(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def associate_people_locations(
    api_key: str,
    company_object: str,
    company_people_attr: str,
    company_locations_attr: str,
    people_object: str,
    location_object: str,
    people_locations_attr: str,
    page_size: int,
    dry_run: bool,
    per_update_sleep_s: float,
    state_file: str,
    audit_file: str = "",
) -> int:
    """Run the sync. Returns a process exit code (0 = clean, 1 = had failures)."""
    client = py_attio.Client(api_key)
    audit = audit_file or None

    # Get current timestamp for this run
    current_run_time = utc_now_iso()

    # Load last run timestamp
    last_run = load_json_state(state_file).get("last_run")

    def _finish_clean() -> int:
        # Dry runs must never advance the incremental window: a later real
        # run still needs to see everything the dry run previewed.
        if dry_run:
            print("DRY-RUN: state file not updated")
            return 0
        if not save_json_state(state_file, {"last_run": current_run_time}):
            print("‼️ State save failed; next run will reprocess this window")
            return 1
        print(f"Saved run timestamp: {current_run_time}")
        return 0

    # Get recently modified people
    recently_modified_people = get_recently_modified_people(
        client, people_object, last_run, page_size
    )

    if not recently_modified_people:
        print("No recently modified people found. Skipping processing.")
        return _finish_clean()

    # Find companies associated with these people (single checkpointed scan)
    target_companies = collect_target_companies(
        client,
        company_object,
        company_people_attr,
        company_locations_attr,
        recently_modified_people,
        page_size,
        checkpoint_file=checkpoint_path_for(state_file),
    )

    if not target_companies:
        print("No companies found associated with recently modified people.")
        return _finish_clean()

    updates_made = 0
    failures = 0
    companies_processed = 0
    people_updated = set()

    print(f"Processing {len(target_companies)} companies with recently modified people")

    for company_id, company_data in target_companies.items():
        companies_processed += 1
        company_name = company_data.get("name", "Unknown")
        person_ids = [p for p in company_data.get("people", []) if p]
        location_ids = list(dict.fromkeys(company_data.get("locations", [])))

        if not person_ids or not location_ids:
            if companies_processed % 10 == 0:
                print(f"📊 Processed {companies_processed} companies so far...")
            continue

        print(
            f"🏢 Processing {company_name}: {len(person_ids)} people, "
            f"{len(location_ids)} locations"
        )

        for person_id in person_ids:
            result = sync_person_locations(
                client,
                people_object,
                location_object,
                people_locations_attr,
                person_id,
                company_id,
                company_name,
                location_ids,
                dry_run,
                audit,
            )
            if result is None:
                failures += 1
            elif result and not dry_run:
                updates_made += 1
                people_updated.add(person_id)
                if per_update_sleep_s > 0:
                    time.sleep(per_update_sleep_s)

    print(
        f"Processed {companies_processed} companies. Updated {updates_made} person "
        f"records ({len(people_updated)} unique people). Failures: {failures}."
    )

    if failures:
        # Do not advance the timestamp: the next run must retry this window.
        # Already-updated people are skipped by the superset check, so the
        # retry only re-attempts what actually failed.
        print(
            f"‼️ {failures} failure(s) — run timestamp NOT advanced; "
            "next run retries this window"
        )
        return 1

    return _finish_clean()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Associate People <> Locations based on Company relations"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("ATTIO_API_KEY", ""),
        help="Attio API key (or set ATTIO_API_KEY)",
    )
    parser.add_argument(
        "--company-object", default="companies", help="Company object slug or ID"
    )
    parser.add_argument(
        "--company-people-attr",
        required=True,
        help="Company->People relationship attribute slug",
    )
    parser.add_argument(
        "--company-locations-attr",
        required=True,
        help="Company->Locations relationship attribute slug",
    )
    parser.add_argument(
        "--people-object", default="people", help="People object slug or ID"
    )
    parser.add_argument(
        "--location-object", default="locations", help="Locations object slug or ID"
    )
    parser.add_argument(
        "--people-locations-attr",
        required=True,
        help="People->Locations relationship attribute slug to set",
    )
    parser.add_argument(
        "--page-size", type=int, default=100, help="Pagination size for companies"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not perform updates, only print intended actions",
    )
    parser.add_argument(
        "--per-update-sleep-s",
        type=float,
        default=0.0,
        help="Sleep seconds after each update to be gentle on rate limits",
    )
    parser.add_argument(
        "--state-file",
        default=".associate_people_locations_state.json",
        help="File to store last run timestamp (default: .associate_people_locations_state.json)",
    )
    parser.add_argument(
        "--audit-file",
        default=".associate_people_locations_audit.jsonl",
        help=(
            "Append-only JSONL audit log of every association attempt "
            "(default: .associate_people_locations_audit.jsonl; "
            "pass empty string to disable)"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.api_key:
        print("Error: ATTIO_API_KEY not set and --api-key not provided")
        sys.exit(1)

    sys.exit(
        associate_people_locations(
            api_key=args.api_key,
            company_object=args.company_object,
            company_people_attr=args.company_people_attr,
            company_locations_attr=args.company_locations_attr,
            people_object=args.people_object,
            location_object=args.location_object,
            people_locations_attr=args.people_locations_attr,
            page_size=args.page_size,
            dry_run=args.dry_run,
            per_update_sleep_s=args.per_update_sleep_s,
            state_file=args.state_file,
            audit_file=args.audit_file,
        )
    )


if __name__ == "__main__":
    main()
