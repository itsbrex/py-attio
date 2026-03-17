"""Console-script entry points for uv-friendly local workflows."""

from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_example(relative_path: str) -> None:
    script_path = _repo_root() / relative_path
    if not script_path.exists():
        raise SystemExit(f"Example script not found: {script_path}")
    runpy.run_path(str(script_path), run_name="__main__")


def run_pytest() -> None:
    """Run pytest via `uv run test`."""
    raise SystemExit(
        subprocess.run([sys.executable, "-m", "pytest", *sys.argv[1:]]).returncode
    )


def list_objects() -> None:
    _run_example("examples/objects/list_objects.py")


def list_lists() -> None:
    _run_example("examples/lists/list_lists.py")


def list_attributes() -> None:
    _run_example("examples/attributes/list_attributes.py")


def list_members() -> None:
    _run_example("examples/workspace_members/list_members.py")


def list_notes() -> None:
    _run_example("examples/notes/list_notes.py")


def create_record() -> None:
    _run_example("examples/records/create_record.py")


def crud_records() -> None:
    _run_example("examples/records/crud_records.py")


def comprehensive_crud_demo() -> None:
    _run_example("examples/comprehensive_crud_demo.py")


def custom_objects() -> None:
    _run_example("examples/objects/custom_objects.py")


def delete_object() -> None:
    _run_example("examples/objects/delete_object.py")


def associate_people_locations() -> None:
    _run_example("examples/relationships/associate_people_locations.py")


def associate_single_company_people_locations() -> None:
    _run_example("examples/relationships/associate_single_company_people_locations.py")
