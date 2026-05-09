#!/usr/bin/env python3
"""
Apply LLM output (from Gemini or any other source) to YAML draft files.

Usage:
    uv run python scripts/apply_llm_output.py --input responses.json
    uv run python scripts/apply_llm_output.py --input responses.json --dry-run

The input JSON should be either:
  - A JSON array where each element has a "filename" field (recommended)
  - A JSON array where each element has an "index" field (legacy, still works)
  - An object with a key like "results" / "companies" / "data" / "items" containing such an array

Example element:
  {
    "filename": "vadatech.yaml",
    "name": "VADATECH",
    "website_url": "https://example.com",
    "linkedin_url": "https://linkedin.com/company/example",
    "careers_url": "https://example.com/careers",
    "description": "Does X and Y.",
    "origin": "local",
    "employees": "11-50",
    "company_type": "product"
  }
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import yaml
from rich.console import Console

from awesome_media.config import (
    ALLOWED_ORIGINS,
    ALLOWED_EMPLOYEE_RANGES,
    ALLOWED_COMPANY_TYPES,
    CONTENT_DIR,
)
from awesome_media.utils.strings import url_to_filename

console = Console()


def mark_checked(data: dict) -> dict:
    """Add _meta.checked_at timestamp so we don't re-check later."""
    data["_meta"] = {"checked_at": datetime.now(timezone.utc).isoformat()}
    return data


def is_checked(path: Path) -> bool:
    """Return True if file already has _meta.checked_at."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        meta = data.get("_meta")
        return isinstance(meta, dict) and bool(meta.get("checked_at"))
    except Exception:
        return False


def sanitize_url(url: str | None) -> str | None:
    if not url:
        return None
    url = str(url).strip()
    if url.lower() in ("null", "none", "n/a", "-", ""):
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def sanitize_choice(val: str | None, allowed: set) -> str | None:
    if not val:
        return None
    val = str(val).strip().lower()
    for a in allowed:
        if val == a.lower():
            return a
    return None


def update_yaml(path: Path, result: dict) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    web = sanitize_url(result.get("website_url"))
    if web:
        if isinstance(data.get("website"), dict):
            data["website"]["url"] = web
        else:
            data["website"] = {"url": web}

    li = sanitize_url(result.get("linkedin_url"))
    if li:
        links = data.get("links", [])
        if not isinstance(links, list):
            links = []
        has_li = any(isinstance(l, dict) and l.get("type") == "linkedin" for l in links)
        if not has_li:
            links.append({"url": li, "type": "linkedin"})
        data["links"] = links

    careers = sanitize_url(result.get("careers_url"))
    if careers:
        links = data.get("links", [])
        if not isinstance(links, list):
            links = []
        has_careers = any(isinstance(l, dict) and l.get("type") == "careers" for l in links)
        if not has_careers:
            links.append({"url": careers, "type": "careers"})
        data["links"] = links

    desc = result.get("description")
    if desc and str(desc).strip().lower() not in ("null", "none", "n/a", ""):
        data["description"] = str(desc).strip()

    origin = sanitize_choice(result.get("origin"), set(ALLOWED_ORIGINS))
    if origin:
        data["origin"] = origin

    employees = sanitize_choice(result.get("employees"), set(ALLOWED_EMPLOYEE_RANGES))
    if employees:
        data["employees"] = employees

    ctype = sanitize_choice(result.get("company_type"), set(ALLOWED_COMPANY_TYPES))
    if ctype:
        data["company_type"] = ctype

    return data


def write_yaml(path: Path, data: dict) -> None:
    def str_representer(dumper, value):
        if "\n" in value:
            return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", value)

    yaml.add_representer(str, str_representer)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def is_complete(data: dict) -> bool:
    for field in ["name", "origin", "employees", "company_type"]:
        v = data.get(field)
        if not v or not str(v).strip() or str(v).strip().startswith("# TODO"):
            return False
    web = data.get("website", {})
    url = web.get("url", "") if isinstance(web, dict) else (web or "")
    if not url or not url.strip() or url.strip().startswith("# TODO"):
        return False
    return True


def load_results(input_path: Path) -> list:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("results", "companies", "data", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        if "filename" in data or "index" in data:
            return [data]
        return []

    raise ValueError(f"Unexpected JSON type: {type(data).__name__}")


def main():
    parser = argparse.ArgumentParser(description="Apply LLM output to YAML drafts")
    parser.add_argument("--input", type=str, required=True, help="JSON file with LLM responses")
    parser.add_argument("--drafts-dir", type=str, default="drafts", help="Drafts directory")
    parser.add_argument("--contents-dir", type=str, default="contents", help="Contents directory")
    parser.add_argument("--include-contents", action="store_true", help="Also scan contents/")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    parser.add_argument(
        "--recheck",
        action="store_true",
        help="Re-check files that already have _meta.checked_at",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    drafts_dir = root / args.drafts_dir
    contents_dir = root / args.contents_dir
    input_path = Path(args.input)

    if not input_path.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        sys.exit(1)

    files = []
    if drafts_dir.exists():
        files.extend(sorted(drafts_dir.glob("*.yaml")))
    if args.include_contents and contents_dir.exists():
        files.extend(sorted(contents_dir.glob("*.yaml")))

    if not files:
        console.print("[yellow]No YAML files found.[/yellow]")
        sys.exit(0)

    # Build filename → path map for stable matching
    file_map = {f.name: f for f in files}

    checked_files = set()
    if not args.recheck:
        for f in files:
            if is_checked(f):
                checked_files.add(str(f))
        if checked_files:
            console.print(f"[yellow]Will skip {len(checked_files)} already-checked files (use --recheck to override).[/yellow]")

    results = load_results(input_path)

    # Map results by filename (primary) or index (legacy fallback)
    result_map = {}
    unmatched = []
    for r in results:
        fname = r.get("filename")
        if fname and fname in file_map:
            result_map[fname] = r
            continue

        # Legacy: match by index
        idx = r.get("index")
        if idx is not None and isinstance(idx, int) and 0 <= idx < len(files):
            legacy_name = files[idx].name
            result_map[legacy_name] = r
            continue

        unmatched.append(r)

    if unmatched:
        console.print(f"[yellow]Warning:[/yellow] {len(unmatched)} results could not be matched to any file.")

    console.print(f"Loaded {len(results)} results, matched {len(result_map)} files.")
    console.print(f"Total files: {len(files)}")

    updated = 0
    moved = 0
    skipped = 0
    skipped_checked_count = 0

    for fname, path in file_map.items():
        result = result_map.get(fname)
        if not result:
            skipped += 1
            continue

        if str(path) in checked_files:
            skipped_checked_count += 1
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        name = data.get("name", path.stem)

        if args.dry_run:
            console.print(f"[cyan]DRY[/cyan] {name}: {result}")
            updated += 1
            continue

        try:
            updated_data = update_yaml(path, result)
            updated_data = mark_checked(updated_data)
            write_yaml(path, updated_data)

            if is_complete(updated_data) and path.parent != contents_dir:
                web = updated_data.get("website", {})
                url = web.get("url", "") if isinstance(web, dict) else web
                expected = url_to_filename(url)
                target_name = expected if expected else path.name
                target = contents_dir / target_name
                if target.exists():
                    console.print(f"[yellow]Exists:[/yellow] {path.name} → {target.name} (deleting draft)")
                    path.unlink()
                else:
                    path.rename(target)
                    moved += 1

            updated += 1
        except Exception as e:
            console.print(f"[red]Failed {path.name}:[/red] {e}")

    console.print(f"\n[bold]Done![/bold]")
    console.print(f"  Updated: {updated}")
    console.print(f"  Moved:   {moved}")
    console.print(f"  Skipped (no result): {skipped}")
    console.print(f"  Skipped (checked):   {skipped_checked_count}")


if __name__ == "__main__":
    main()
