#!/usr/bin/env python3

"""
Associate People <> Locations based on existing Company <> People and Company <> Locations

This script:
- Iterates Companies, reads their related People and Locations
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
    --dry-run

Notes:
- Attribute slugs are workspace-specific. Confirm the three slugs:
  1) Company -> People relationship attribute slug (e.g. "people")
  2) Company -> Locations relationship attribute slug (e.g. "locations")
  3) People -> Locations relationship attribute slug (e.g. "locations")
- The script deduplicates relations and only updates when new links are needed.
"""

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Set

# Ensure we can import the local package when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

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
):
    client = py_attio.Client(api_key)

    updates_made = 0
    companies_seen = 0
    people_considered: Set[str] = set()

    for company in client.paginate_records(company_object, page_size=page_size):
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
    )


if __name__ == "__main__":
    main()
