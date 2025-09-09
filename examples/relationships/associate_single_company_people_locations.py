#!/usr/bin/env python3

"""
Associate People <> Locations for a single Company

This script takes a company identifier (domain or Attio URL) and:
- Finds the company record
- Gets all associated People and Locations for that company
- Updates each Person to include all the Company's Locations

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
- For domain matching, the script searches for companies with matching domain in their primary domain field
- For Attio URLs, it extracts the company record ID from the URL
- Attribute slugs are workspace-specific - confirm the slugs match your schema
"""

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

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


def extract_company_id_from_url(url: str) -> Optional[str]:
    """Extract company record ID from Attio URL.

    Expected format: https://app.attio.com/{workspace}/company/{record_id}/...
    """
    try:
        parsed = urlparse(url)
        if "attio.com" not in parsed.netloc:
            return None

        # Split path and look for company/{id} pattern
        path_parts = [p for p in parsed.path.split("/") if p]
        for i, part in enumerate(path_parts):
            if part == "company" and i + 1 < len(path_parts):
                potential_id = path_parts[i + 1]
                # Basic UUID validation (36 chars with hyphens)
                if len(potential_id) == 36 and potential_id.count("-") == 4:
                    return potential_id
        return None
    except Exception:
        return None


def find_company_by_domain(
    client: py_attio.Client,
    domain: str,
    company_object: str,
    domain_attr: str = "primary_domain",
) -> Optional[Dict[str, Any]]:
    """Find company record by domain name."""
    try:
        # Query companies with domain filter
        query_payload = {
            "filter": {domain_attr: {"any_of": [domain]}},
            "limit": 10,  # Should be unique, but limit results
        }

        response = client.list_records(company_object, query_payload)
        companies = response.get("data", [])

        if not companies:
            return None

        # Return first match (domains should be unique)
        return companies[0]

    except Exception as e:
        print(f"‼️ FIXME: Error searching for company domain '{domain}': {e}")
        return None


def find_company_by_id(
    client: py_attio.Client, company_id: str, company_object: str
) -> Optional[Dict[str, Any]]:
    """Find company record by ID."""
    try:
        response = client.get_record(company_object, company_id)
        return response.get("data")
    except Exception as e:
        print(f"‼️ FIXME: Error fetching company ID '{company_id}': {e}")
        return None


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
):
    client = py_attio.Client(api_key)

    # Determine if input is URL or domain
    company_record = None
    if company_identifier.startswith("http"):
        # Extract company ID from URL
        company_id = extract_company_id_from_url(company_identifier)
        if not company_id:
            print(f"❌ Could not extract company ID from URL: {company_identifier}")
            return
        print(f"🔍 Looking up company by ID: {company_id}")
        company_record = find_company_by_id(client, company_id, company_object)
    else:
        # Treat as domain
        print(f"🔍 Looking up company by domain: {company_identifier}")
        company_record = find_company_by_domain(
            client, company_identifier, company_object, domain_attr
        )

    if not company_record:
        print(f"❌ Company not found: {company_identifier}")
        return

    # Extract company info
    company_id = company_record.get("id", {}).get("record_id")
    company_values = company_record.get("values", {}) or {}

    # Get company name for display - handle different possible structures
    company_name = "Unknown"

    # Try common name attribute patterns
    name_candidates = ["name", "company_name", "title"]
    for name_attr in name_candidates:
        if name_attr in company_values and company_values[name_attr]:
            name_value = company_values[name_attr]
            if isinstance(name_value, list) and name_value:
                # Handle list format - extract value from first item
                first_item = name_value[0]
                if isinstance(first_item, dict):
                    company_name = first_item.get("value", str(first_item))
                else:
                    company_name = str(first_item)
            elif isinstance(name_value, str):
                company_name = name_value
            elif isinstance(name_value, dict):
                company_name = name_value.get("value", str(name_value))
            else:
                company_name = str(name_value)
            break

    print(f"✅ Found company: {company_name} (ID: {company_id})")

    # Extract related people and locations
    people_links = company_values.get(company_people_attr, [])
    location_links = company_values.get(company_locations_attr, [])

    person_ids = extract_linked_record_ids(people_links)
    location_ids = extract_linked_record_ids(location_links)

    print(f"📊 Company has {len(person_ids)} people and {len(location_ids)} locations")

    if not person_ids:
        print("⚠️ No people associated with this company")
        return

    if not location_ids:
        print("⚠️ No locations associated with this company")
        return

    unique_location_ids = list(dict.fromkeys(location_ids))
    updates_made = 0

    # Update each person
    for person_id in person_ids:
        if not person_id:
            continue

        # Fetch person's current locations to avoid overwriting unrelated links
        try:
            person = client.get_record(people_object, person_id)
        except Exception as e:
            print(f"‼️ FIXME: Failed to fetch person {person_id}: {e}")
            continue

        person_values: Dict[str, Any] = person.get("data", {}).get("values", {}) or {}

        # Get person name for display
        person_name = "Unknown"
        if "name" in person_values and person_values["name"]:
            name_data = (
                person_values["name"][0]
                if isinstance(person_values["name"], list)
                else {}
            )
            if isinstance(name_data, dict):
                first = name_data.get("first_name", "")
                last = name_data.get("last_name", "")
                person_name = f"{first} {last}".strip() or "Unknown"

        existing_links = person_values.get(people_locations_attr, [])
        existing_location_ids = set(extract_linked_record_ids(existing_links))

        # Compute union
        desired_ids = list(existing_location_ids.union(unique_location_ids))

        # No changes needed
        if existing_location_ids.issuperset(unique_location_ids):
            print(f"✅ {person_name} already has all company locations")
            continue

        new_locations = set(unique_location_ids) - existing_location_ids
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
                f"DRY-RUN: Would update {person_name} ({person_id}) to add {len(new_locations)} new locations"
            )
        else:
            try:
                client.update_record(people_object, person_id, payload)
                updates_made += 1
                print(
                    f"✅ Updated {person_name} with {len(new_locations)} new locations"
                )
                if per_update_sleep_s > 0:
                    time.sleep(per_update_sleep_s)
            except Exception as e:
                print(f"‼️ FIXME: Failed to update {person_name} ({person_id}): {e}")

    print(f"\n🎉 Completed! Updated {updates_made} people with company locations.")


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
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.api_key:
        print("Error: ATTIO_API_KEY not set and --api-key not provided")
        sys.exit(1)

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
    )


if __name__ == "__main__":
    main()
