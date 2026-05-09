#!/usr/bin/env python3
"""
Find incomplete YAML content files and report what's missing.

Usage:
    uv run python scripts/find_incomplete_yamls.py
    uv run python scripts/find_incomplete_yamls.py --json report.json
    uv run python scripts/find_incomplete_yamls.py --only-drafts
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import yaml
from rich.console import Console
from rich.table import Table

from awesome_media.config import (
    ALLOWED_ORIGINS,
    ALLOWED_EMPLOYEE_RANGES,
    ALLOWED_COMPANY_TYPES,
    CONTENT_DIR,
)

console = Console()


def _is_checked(data: dict) -> str | None:
    """Return checked timestamp if file has _meta.checked_at, else None."""
    meta = data.get("_meta")
    if isinstance(meta, dict):
        return meta.get("checked_at")
    return None


def is_empty(val) -> bool:
    """Check if a YAML field value is effectively empty."""
    if val is None:
        return True
    if isinstance(val, str):
        return not val.strip() or val.strip().startswith("# TODO")
    if isinstance(val, list):
        return len(val) == 0
    if isinstance(val, dict):
        return all(is_empty(v) for v in val.values())
    return False


def check_file(path: Path) -> dict:
    """Return a dict with missing fields for a given YAML file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        return {"file": str(path), "error": str(e)}

    missing = []

    # Required scalar fields
    for field in ["name", "origin", "employees", "company_type"]:
        if is_empty(data.get(field)):
            missing.append(field)

    # Website URL
    web = data.get("website")
    url = ""
    if isinstance(web, dict):
        url = web.get("url", "")
    elif isinstance(web, str):
        url = web
    if is_empty(url):
        missing.append("website.url")

    # Description
    if is_empty(data.get("description")):
        missing.append("description")

    # Validate allowed values
    invalid = []
    origin = data.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        invalid.append(f"origin='{origin}'")

    emp = data.get("employees")
    if emp and emp not in ALLOWED_EMPLOYEE_RANGES:
        invalid.append(f"employees='{emp}'")

    ctype = data.get("company_type")
    if ctype and ctype not in ALLOWED_COMPANY_TYPES:
        invalid.append(f"company_type='{ctype}'")

    checked_at = _is_checked(data)
    return {
        "file": str(path),
        "name": data.get("name", "???"),
        "missing": missing,
        "invalid": invalid,
        "complete": len(missing) == 0 and len(invalid) == 0,
        "checked": checked_at is not None,
        "checked_at": checked_at,
    }


def main():
    parser = argparse.ArgumentParser(description="Find incomplete YAML content files")
    parser.add_argument("--json", type=str, help="Write report to JSON file")
    parser.add_argument("--only-drafts", action="store_true", help="Only scan drafts/")
    parser.add_argument(
        "--only-contents", action="store_true", help="Only scan contents/"
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    dirs = []
    if not args.only_drafts:
        dirs.append(CONTENT_DIR)
    if not args.only_contents:
        drafts_dir = root / "drafts"
        if drafts_dir.exists():
            dirs.append(drafts_dir)

    results = []
    for d in dirs:
        for path in sorted(d.glob("*.yaml")):
            if path.name.lower().startswith("example"):
                continue
            results.append(check_file(path))

    incomplete = [r for r in results if not r.get("complete")]
    complete = [r for r in results if r.get("complete")]

    # Print summary table
    table = Table(title="YAML Completeness Report")
    table.add_column("Location", style="cyan")
    table.add_column("Total", justify="right")
    table.add_column("Complete", justify="right", style="green")
    table.add_column("Incomplete", justify="right", style="red")
    table.add_column("Checked", justify="right", style="yellow")
    table.add_column("Unchecked", justify="right", style="magenta")

    for d in dirs:
        d_results = [r for r in results if Path(r["file"]).parent == d]
        d_complete = sum(1 for r in d_results if r.get("complete"))
        d_incomplete = len(d_results) - d_complete
        d_checked = sum(1 for r in d_results if r.get("checked"))
        d_unchecked = len(d_results) - d_checked
        table.add_row(str(d), str(len(d_results)), str(d_complete), str(d_incomplete), str(d_checked), str(d_unchecked))

    console.print(table)

    if incomplete:
        checked_incomplete = [r for r in incomplete if r.get("checked")]
        unchecked_incomplete = [r for r in incomplete if not r.get("checked")]

        console.print(f"\n[bold red]Incomplete fields:[/bold red] (checked: {len(checked_incomplete)}, unchecked: {len(unchecked_incomplete)})")
        from collections import Counter
        field_counts = Counter(f for r in incomplete for f in r["missing"])
        for field, count in field_counts.most_common():
            console.print(f"  {field}: {count}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"complete": complete, "incomplete": incomplete}, f, indent=2)
        console.print(f"\n[green]Report written to {args.json}[/green]")

    # Return non-zero if there are unchecked incomplete files
    has_unchecked = any(not r.get("checked") for r in incomplete)
    sys.exit(0 if not has_unchecked else 1)


if __name__ == "__main__":
    main()
