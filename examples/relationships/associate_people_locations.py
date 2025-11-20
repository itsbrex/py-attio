#!/usr/bin/env python3

"""
Associate People <> Locations based on existing Company <> People and Company <> Locations

This script:
- Efficiently processes only companies with recently created/updated people
- Uses date-based filtering to avoid reprocessing unchanged data
- Updates each related Person to include the Company's Locations in a chosen People->Locations relationship attribute

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
3. Finds companies associated with those recently modified people
4. Only processes those specific companies (much more efficient!)
5. Saves new timestamp after successful completion

Notes:
- Attribute slugs are workspace-specific. Confirm the three slugs:
  1) Company -> People relationship attribute slug (e.g. "people")
  2) Company -> Locations relationship attribute slug (e.g. "locations")
  3) People -> Locations relationship attribute slug (e.g. "locations")
- The script deduplicates relations and only updates when new links are needed.
- First run processes all people; subsequent runs are incremental based on timestamps.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Optional

# Ensure we can import the local package when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Load .env file if it exists
def load_env_file(env_path: str = ".env"):
    """Load environment variables from .env file if it exists."""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value

# Load .env from repo root
load_env_file(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import py_attio  # noqa: E402


def extract_linked_record_ids(items: List[Dict[str, Any]]) -> List[str]:
    """Extract target record IDs from a relationship attribute value array.

    Supports common shapes:
    - {"target_record_id": "..."}
    - {"record_id": "..."}
    - {"id": {"record_id": "..."}}
    - {"target": {"record_id": "..."}}
    """
    ids: List[str] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        if "target_record_id" in item and item["target_record_id"]:
            ids.append(item["target_record_id"])  # type: ignore[arg-type]
            continue
        if "record_id" in item and item["record_id"]:
            ids.append(item["record_id"])  # type: ignore[arg-type]
            continue
        target = item.get("target")
        if isinstance(target, dict) and target.get("record_id"):
            ids.append(target["record_id"])  # type: ignore[index]
            continue
        id_obj = item.get("id")
        if isinstance(id_obj, dict) and id_obj.get("record_id"):
            ids.append(id_obj["record_id"])  # type: ignore[index]
            continue
    return ids


def build_relationship_value(
    ids: List[str], target_object: str
) -> List[Dict[str, str]]:
    """Build relationship attribute payload items from record IDs.

    Uses the documented shape for record relationships in write payloads:
    [{"target_object": <object_slug>, "target_record_id": <record_id>}]
    """
    unique_ids: List[str] = list(dict.fromkeys([i for i in ids if i]))
    return [
        {"target_object": target_object, "target_record_id": record_id}
        for record_id in unique_ids
    ]


def load_last_run_timestamp(state_file: str) -> Optional[str]:
    """Load the timestamp of the last successful run."""
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
                return data.get('last_run')
    except Exception as e:
        print(f"Warning: Failed to load state file {state_file}: {e}")
    return None


def save_last_run_timestamp(state_file: str, timestamp: str):
    """Save the timestamp of the current run."""
    try:
        data = {'last_run': timestamp}
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save state file {state_file}: {e}")


def get_recently_modified_people(
    client: py_attio.Client,
    people_object: str,
    last_run: Optional[str],
    page_size: int,
) -> Set[str]:
    """Get people IDs that were created or updated since last run."""
    people_ids: Set[str] = set()
    
    if not last_run:
        print("No previous run found - this will process all people initially")
        # If no last run, get all people (initial run)
        for person in client.paginate_records(people_object, page_size=page_size):
            person_id = person.get("id")
            if person_id:
                # Handle both string IDs and dict IDs with record_id
                if isinstance(person_id, dict):
                    record_id = person_id.get("record_id")
                    if record_id:
                        people_ids.add(record_id)
                else:
                    people_ids.add(person_id)
        return people_ids
    
    # Filter by created_at >= last_run
    created_filter = {
        "filter": {
            "created_at": {
                "gte": last_run
            }
        }
    }
    
    # Filter by updated_at >= last_run  
    updated_filter = {
        "filter": {
            "updated_at": {
                "gte": last_run
            }
        }
    }
    
    print(f"Fetching people created since {last_run}")
    try:
        for person in client.paginate_records(people_object, page_size=page_size, **created_filter):
            person_id = person.get("id")
            if person_id:
                # Handle both string IDs and dict IDs with record_id
                if isinstance(person_id, dict):
                    record_id = person_id.get("record_id")
                    if record_id:
                        people_ids.add(record_id)
                else:
                    people_ids.add(person_id)
    except Exception as e:
        print(f"Warning: Failed to filter by created_at: {e}")
    
    print(f"Fetching people updated since {last_run}")
    try:
        for person in client.paginate_records(people_object, page_size=page_size, **updated_filter):
            person_id = person.get("id")
            if person_id:
                # Handle both string IDs and dict IDs with record_id
                if isinstance(person_id, dict):
                    record_id = person_id.get("record_id")
                    if record_id:
                        people_ids.add(record_id)
                else:
                    people_ids.add(person_id)
    except Exception as e:
        print(f"Warning: Failed to filter by updated_at: {e}")
    
    print(f"Found {len(people_ids)} people modified since last run")
    return people_ids


def load_checkpoint(checkpoint_file: str) -> Dict[str, Any]:
    """Load checkpoint data from file."""
    try:
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load checkpoint file {checkpoint_file}: {e}")
    return {}


def save_checkpoint(checkpoint_file: str, data: Dict[str, Any]):
    """Save checkpoint data to file."""
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save checkpoint file {checkpoint_file}: {e}")


def get_companies_for_people(
    client: py_attio.Client,
    company_object: str,
    company_people_attr: str,
    target_people_ids: Set[str],
    page_size: int,
    checkpoint_file: Optional[str] = None,
) -> Set[str]:
    """Find companies that have relationships with the target people."""
    company_ids: Set[str] = set()
    companies_seen = 0

    # Load checkpoint if available
    checkpoint = {}
    if checkpoint_file:
        checkpoint = load_checkpoint(checkpoint_file)
        if checkpoint.get('company_ids'):
            company_ids = set(checkpoint['company_ids'])
            companies_seen = checkpoint.get('companies_seen', 0)
            print(f"Resuming from checkpoint: {companies_seen} companies scanned, {len(company_ids)} relevant found")

    try:
        for company in client.paginate_records(company_object, page_size=page_size, delay_between_pages=0.2):
            companies_seen += 1

            # Save checkpoint every 500 companies
            if checkpoint_file and companies_seen % 500 == 0:
                checkpoint_data = {
                    'companies_seen': companies_seen,
                    'company_ids': list(company_ids)
                }
                save_checkpoint(checkpoint_file, checkpoint_data)

            if companies_seen % 50 == 0:
                print(f"Scanned {companies_seen} companies, found {len(company_ids)} relevant...")

            company_values: Dict[str, Any] = company.get("values", {}) or {}
            people_links = company_values.get(company_people_attr, [])
            person_ids = extract_linked_record_ids(people_links)

            # Check if any of this company's people are in our target set
            if any(person_id in target_people_ids for person_id in person_ids):
                company_id = company["id"]
                if isinstance(company_id, dict):
                    company_id = company_id.get("record_id")
                if company_id:
                    company_ids.add(company_id)
    except Exception as e:
        # Save checkpoint on error before raising
        if checkpoint_file:
            checkpoint_data = {
                'companies_seen': companies_seen,
                'company_ids': list(company_ids),
                'error': str(e)
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            print(f"💾 Checkpoint saved due to error. Progress: {companies_seen} companies scanned")
        raise

    # Clear checkpoint on successful completion
    if checkpoint_file and os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    print(f"Found {len(company_ids)} companies associated with recently modified people")
    return company_ids


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
):
    client = py_attio.Client(api_key)
    
    # Get current timestamp for this run
    current_run_time = datetime.now(timezone.utc).isoformat()
    
    # Load last run timestamp
    last_run = load_last_run_timestamp(state_file)
    
    # Get recently modified people
    recently_modified_people = get_recently_modified_people(
        client, people_object, last_run, page_size
    )
    
    if not recently_modified_people:
        print("No recently modified people found. Skipping processing.")
        save_last_run_timestamp(state_file, current_run_time)
        return
    
    # Find companies associated with these people
    checkpoint_file = state_file.replace('.json', '_checkpoint.json')
    target_companies = get_companies_for_people(
        client, company_object, company_people_attr, recently_modified_people, page_size,
        checkpoint_file=checkpoint_file
    )
    
    if not target_companies:
        print("No companies found associated with recently modified people.")
        save_last_run_timestamp(state_file, current_run_time)
        return

    updates_made = 0
    companies_seen = 0
    people_considered: Set[str] = set()
    
    print(f"Processing {len(target_companies)} companies with recently modified people")

    # Only process companies that have recently modified people
    for company in client.paginate_records(company_object, page_size=page_size):
        company_id = company.get("id")
        if isinstance(company_id, dict):
            company_id = company_id.get("record_id")
        if company_id not in target_companies:
            continue
        companies_seen += 1
        company_values: Dict[str, Any] = company.get("values", {}) or {}

        # Get company name for logging
        company_name = "Unknown"
        if "name" in company_values and company_values["name"]:
            name_value = company_values["name"]
            if isinstance(name_value, list) and name_value:
                first_item = name_value[0]
                if isinstance(first_item, dict):
                    company_name = first_item.get("value", str(first_item))
                else:
                    company_name = str(first_item)

        people_links = company_values.get(company_people_attr, [])
        location_links = company_values.get(company_locations_attr, [])

        person_ids = extract_linked_record_ids(people_links)
        location_ids = extract_linked_record_ids(location_links)

        if not person_ids or not location_ids:
            if companies_seen % 10 == 0:  # Log every 10 companies processed
                print(f"📊 Processed {companies_seen} companies so far...")
            continue

        print(
            f"🏢 Processing {company_name}: {len(person_ids)} people, {len(location_ids)} locations"
        )

        unique_location_ids = list(dict.fromkeys(location_ids))

        for person_id in person_ids:
            if not person_id:
                continue
            # Fetch person's current locations to avoid overwriting unrelated links
            try:
                person = client.get_record(people_object, person_id)
            except Exception as e:
                print(f"‼️ FIXME: Failed to fetch person {person_id}: {e}")
                continue

            person_values: Dict[str, Any] = (
                person.get("data", {}).get("values", {}) or {}
            )
            existing_links = person_values.get(people_locations_attr, [])
            existing_location_ids = set(extract_linked_record_ids(existing_links))

            # Compute union
            desired_ids = list(existing_location_ids.union(unique_location_ids))

            # No changes needed
            if existing_location_ids.issuperset(unique_location_ids):
                continue

            payload = {
                "data": {
                    "values": {
                        people_locations_attr: build_relationship_value(
                            desired_ids, location_object
                        )
                    }
                }
            }

            if dry_run:
                print(
                    f"DRY-RUN: Would update {people_object}/{person_id} set '{people_locations_attr}' with {len(desired_ids)} locations (adding {len(set(unique_location_ids) - existing_location_ids)})"
                )
            else:
                try:
                    client.update_record(people_object, person_id, payload)
                    updates_made += 1
                    people_considered.add(person_id)
                    new_locations_count = len(
                        set(unique_location_ids) - existing_location_ids
                    )
                    print(
                        f"✅ Updated person {person_id} with {new_locations_count} new locations"
                    )
                    if per_update_sleep_s > 0:
                        time.sleep(per_update_sleep_s)
                except Exception as e:
                    print(
                        f"‼️ FIXME: Failed to update {people_object}/{person_id} for locations: {e}"
                    )

    print(
        f"Processed {companies_seen} companies. Updated {updates_made} person records. Considered {len(people_considered)} unique people."
    )
    
    # Save timestamp of successful run
    if not dry_run:
        save_last_run_timestamp(state_file, current_run_time)
        print(f"Saved run timestamp: {current_run_time}")


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
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.api_key:
        print("Error: ATTIO_API_KEY not set and --api-key not provided")
        sys.exit(1)

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
    )


if __name__ == "__main__":
    main()
