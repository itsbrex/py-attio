"""Shared helpers for relationship-sync scripts and other Attio workflows.

These utilities cover the recurring needs of long-running sync scripts:
extracting record IDs from the several shapes Attio returns, building write
payloads, durable (atomic, fsync'd) state files, and an append-only JSONL
audit trail so association changes always leave a paper trail.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from a .env file if it exists.

    Values already present in the environment win over .env entries.
    """
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip("\"'")
                    os.environ.setdefault(key, value)


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
            ids.append(item["target_record_id"])
            continue
        if "record_id" in item and item["record_id"]:
            ids.append(item["record_id"])
            continue
        target = item.get("target")
        if isinstance(target, dict) and target.get("record_id"):
            ids.append(target["record_id"])
            continue
        id_obj = item.get("id")
        if isinstance(id_obj, dict) and id_obj.get("record_id"):
            ids.append(id_obj["record_id"])
            continue
    return ids


def extract_record_id(record: Dict[str, Any]) -> Optional[str]:
    """Extract a record's own ID, handling both string and dict id shapes."""
    record_id = record.get("id")
    if isinstance(record_id, dict):
        return record_id.get("record_id")
    return record_id


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


def build_location_value(
    line_1: Optional[str] = None,
    line_2: Optional[str] = None,
    line_3: Optional[str] = None,
    line_4: Optional[str] = None,
    locality: Optional[str] = None,
    region: Optional[str] = None,
    postcode: Optional[str] = None,
    country_code: Optional[str] = None,
    latitude: Optional[str] = None,
    longitude: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a `location` complex-type value with all 10 keys present.

    Attio rejects partial location objects -- every key must be present, using
    None where a component is unknown. ``region`` is the state/province,
    ``locality`` the city, and ``country_code`` the ISO 3166-1 alpha-2 code.
    Empty strings are normalized to None so blank source fields don't leak
    through as "".
    """

    def _clean(v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip() if isinstance(v, str) else v
        return v or None

    return {
        "line_1": _clean(line_1),
        "line_2": _clean(line_2),
        "line_3": _clean(line_3),
        "line_4": _clean(line_4),
        "locality": _clean(locality),
        "region": _clean(region),
        "postcode": _clean(postcode),
        "country_code": _clean(country_code),
        "latitude": latitude,
        "longitude": longitude,
    }


def build_record_payload(
    values: Dict[str, Any], drop_none: bool = True
) -> Dict[str, Any]:
    """Wrap an attribute-slug->value map in the Attio create/update envelope.

    Returns ``{"data": {"values": ...}}``. With ``drop_none`` (default), keys
    whose value is None are removed so blank scalars are never sent -- note
    complex types built via ``build_location_value`` keep their inner None keys,
    which Attio requires.
    """
    if drop_none:
        values = {k: v for k, v in values.items() if v is not None}
    return {"data": {"values": values}}


def get_first_value(values: Dict[str, Any], attr: str, default: str = "Unknown") -> str:
    """Extract a display string from an Attio value array."""
    raw = values.get(attr)
    if isinstance(raw, list) and raw:
        first_item = raw[0]
        if isinstance(first_item, dict):
            return first_item.get("value", str(first_item))
        return str(first_item)
    if isinstance(raw, str) and raw:
        return raw
    return default


def utc_now_iso() -> str:
    """Current UTC time in Attio-friendly RFC3339 seconds precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_attio_timestamp(value: str) -> str:
    """Normalize timestamps to Attio-friendly UTC RFC3339 format (seconds precision)."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    as_utc = parsed.astimezone(timezone.utc)
    return as_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    """Write JSON to disk atomically (temp file + fsync + rename).

    A crash mid-write can never corrupt or truncate the target file.
    """
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def load_json_state(path: str) -> Dict[str, Any]:
    """Load a JSON state/checkpoint file, returning {} when missing or corrupt."""
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load state file {path}: {e}")
    return {}


def save_json_state(path: str, data: Dict[str, Any]) -> bool:
    """Save a JSON state/checkpoint file atomically. Returns True on success.

    A failed save must be surfaced to the caller: silently losing it would
    make the next run reprocess everything (or worse, skip a window).
    """
    try:
        atomic_write_json(path, data)
        return True
    except Exception as e:
        print(f"Warning: Failed to save state file {path}: {e}")
        return False


def checkpoint_path_for(state_file: str) -> str:
    """Derive the checkpoint path without ever colliding with the state file."""
    return f"{state_file}.checkpoint"


def append_audit_entry(audit_file: Optional[str], entry: Dict[str, Any]) -> None:
    """Append one entry to the JSONL audit log (fsync'd, append-only).

    The audit log is the durable paper trail of every association attempt;
    a failure to write it is loud but never aborts the sync itself.
    """
    if not audit_file:
        return
    entry = {"ts": utc_now_iso(), **entry}
    try:
        with open(audit_file, "a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"Warning: Failed to write audit log {audit_file}: {e}")
