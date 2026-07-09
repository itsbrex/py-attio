#!/usr/bin/env python3

"""
Associate People <> Locations for a single Company

This script takes a company identifier (domain or Attio URL) and:
- Finds the company record
- Gets all associated People and Locations for that company
- Updates each Person to include all the Company's Locations
- Appends every attempted update to an append-only JSONL audit log

Usage:
  export ATTIO_API_KEY=...  # or pass --api-key

  # Using domain
  python examples/relationships/associate_single_company_people_locations.py \
    --company google.com \
    --company-people-attr people \
    --company-locations-attr locations \
    --people-locations-attr locations \
    --dry-run

  # Using Attio URL
  python examples/relationships/associate_single_company_people_locations.py \
    --company "https://app.attio.com/workspace/company/00000000-0000-0000-0000-000000000000/overview" \
    --company-people-attr people \
    --company-locations-attr locations \
    --people-locations-attr locations \
    --dry-run

Notes:
- For domain matching, the script searches for companies with matching domain
  in their primary domain field
- For Attio URLs, it extracts the company record ID from the URL
- Attribute slugs are workspace-specific - confirm the slugs match your schema
- Exits non-zero when any person fetch/update fails so callers can retry
"""

import argparse
import os
import sys
import time

# Ensure we can import the local package when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import py_attio  # noqa: E402
from py_attio.lookup import (  # noqa: E402
    extract_company_id_from_url,
    find_company_by_domain,
    find_company_by_id,
)
from py_attio.relationships import sync_person_locations  # noqa: E402
from py_attio.utils import (  # noqa: E402
    extract_linked_record_ids,
    extract_record_id,
    get_first_value,
    load_env_file,
)

# Load .env from repo root (already-exported env vars win)
load_env_file(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def associate_company_people_locations(
    api_key: str,
    company_identifier: str,
    company_object: str,
    company_people_attr: str,
    company_locations_attr: str,
    people_object: str,
    location_object: str,
    people_locations_attr: str,
    domain_attr: str,
    dry_run: bool,
    per_update_sleep_s: float,
    audit_file: str = "",
) -> int:
    """Run the single-company sync. Returns a process exit code."""
    client = py_attio.Client(api_key)
    audit = audit_file or None

    # Determine if input is URL or domain
    company_record = None
    if company_identifier.startswith("http"):
        company_id = extract_company_id_from_url(company_identifier)
        if not company_id:
            print(f"❌ Could not extract company ID from URL: {company_identifier}")
            return 1
        print(f"🔍 Looking up company by ID: {company_id}")
        company_record = find_company_by_id(client, company_id, company_object)
    else:
        print(f"🔍 Looking up company by domain: {company_identifier}")
        company_record = find_company_by_domain(
            client, company_identifier, company_object, domain_attr
        )

    if not company_record:
        print(f"❌ Company not found: {company_identifier}")
        return 1

    # Extract company info
    company_id = extract_record_id(company_record)
    company_values = company_record.get("values", {}) or {}
    company_name = get_first_value(company_values, "name")

    print(f"✅ Found company: {company_name} (ID: {company_id})")

    # Extract related people and locations
    person_ids = extract_linked_record_ids(company_values.get(company_people_attr, []))
    location_ids = extract_linked_record_ids(
        company_values.get(company_locations_attr, [])
    )

    print(f"📊 Company has {len(person_ids)} people and {len(location_ids)} locations")

    if not person_ids:
        print("⚠️ No people associated with this company")
        return 0

    if not location_ids:
        print("⚠️ No locations associated with this company")
        return 0

    unique_location_ids = list(dict.fromkeys(location_ids))
    updates_made = 0
    failures = 0

    for person_id in person_ids:
        if not person_id:
            continue
        result = sync_person_locations(
            client,
            people_object,
            location_object,
            people_locations_attr,
            person_id,
            company_id or "",
            company_name,
            unique_location_ids,
            dry_run,
            audit,
        )
        if result is None:
            failures += 1
        elif result and not dry_run:
            updates_made += 1
            if per_update_sleep_s > 0:
                time.sleep(per_update_sleep_s)

    print(
        f"\n🎉 Completed! Updated {updates_made} people with company locations. "
        f"Failures: {failures}."
    )
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Associate People <> Locations for a single Company"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("ATTIO_API_KEY", ""),
        help="Attio API key (or set ATTIO_API_KEY)",
    )
    parser.add_argument(
        "--company",
        required=True,
        help="Company domain (e.g. 'google.com') or Attio URL",
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
        "--domain-attr",
        default="primary_domain",
        help="Company domain attribute slug for domain searches",
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
        "--audit-file",
        default=".associate_people_locations_audit.jsonl",
        help=(
            "Append-only JSONL audit log of every association attempt "
            "(pass empty string to disable)"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.api_key:
        print("Error: ATTIO_API_KEY not set and --api-key not provided")
        sys.exit(1)

    sys.exit(
        associate_company_people_locations(
            api_key=args.api_key,
            company_identifier=args.company,
            company_object=args.company_object,
            company_people_attr=args.company_people_attr,
            company_locations_attr=args.company_locations_attr,
            people_object=args.people_object,
            location_object=args.location_object,
            people_locations_attr=args.people_locations_attr,
            domain_attr=args.domain_attr,
            dry_run=args.dry_run,
            per_update_sleep_s=args.per_update_sleep_s,
            audit_file=args.audit_file,
        )
    )


if __name__ == "__main__":
    main()
