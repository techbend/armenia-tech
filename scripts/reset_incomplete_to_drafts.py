#!/usr/bin/env python3
"""
Move incomplete YAML files from contents/ back to drafts/ and reset fields for AI re-processing.

A file is considered complete ONLY if it has ALL of:
- name (non-empty)
- description (non-empty)
- at least one link of any kind (website.url OR any entry in links[])

employees, origin, company_type are optional / nice-to-have.

After moving, _meta.checked_at is cleared from ALL draft files (existing + newly moved).

Usage:
    uv run python scripts/reset_incomplete_to_drafts.py
    uv run python scripts/reset_incomplete_to_drafts.py --dry-run
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import yaml
from rich.console import Console

console = Console()


def is_empty(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        return not val.strip() or val.strip().startswith("# TODO")
    return False


def has_any_link(data: dict) -> bool:
    """True if there's a website.url OR any entry in the links array."""
    web = data.get("website")
    if isinstance(web, dict):
        url = web.get("url", "")
    elif isinstance(web, str):
        url = web
    else:
        url = ""
    if url and url.strip() and not url.strip().startswith("# TODO"):
        return True

    links = data.get("links", [])
    if isinstance(links, list) and len(links) > 0:
        return True

    return False


def has_description(data: dict) -> bool:
    desc = data.get("description", "")
    return bool(desc and str(desc).strip() and not str(desc).strip().startswith("# TODO"))


def has_name(data: dict) -> bool:
    name = data.get("name", "")
    return bool(name and str(name).strip() and not str(name).strip().startswith("# TODO"))


def reset_fields(data: dict) -> dict:
    """Reset website, links, description, and _meta for AI re-processing."""
    # Keep: name, origin, employees, company_type, tags
    # Reset: website, links, description, _meta
    data["website"] = {"url": ""}
    if "links" in data:
        del data["links"]
    data["description"] = ""
    if "_meta" in data:
        del data["_meta"]
    return data


def write_yaml(path: Path, data: dict) -> None:
    def str_representer(dumper, value):
        if "\n" in value:
            return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", value)

    yaml.add_representer(str, str_representer)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser(description="Reset incomplete files to drafts for AI re-processing")
    parser.add_argument("--dry-run", action="store_true", help="Don't move or modify files")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    contents_dir = root / "contents"
    drafts_dir = root / "drafts"
    drafts_dir.mkdir(exist_ok=True)

    files = sorted(contents_dir.glob("*.yaml"))
    moved = 0
    skipped = 0

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        name = data.get("name", path.stem)
        has_name_field = has_name(data)
        has_link = has_any_link(data)
        has_desc = has_description(data)

        # Keep if: name + description + at least one link (website or links[])
        if has_name_field and has_link and has_desc:
            skipped += 1
            continue

        # Determine target path in drafts (use same filename)
        target = drafts_dir / path.name
        if target.exists():
            console.print(f"[yellow]Exists in drafts:[/yellow] {path.name} — skipping")
            continue

        if args.dry_run:
            console.print(f"[cyan]DRY[/cyan] Would reset + move: {name} (name={has_name_field}, links={has_link}, desc={has_desc})")
            moved += 1
            continue

        # Reset fields and write to drafts
        reset_data = reset_fields(data.copy())
        write_yaml(target, reset_data)

        # Remove from contents
        path.unlink()

        moved += 1
        console.print(f"[green]Reset + moved:[/green] {name} → drafts/{target.name}")

    # Clear _meta from ALL draft files (existing + newly moved)
    cleared_meta = 0
    for draft_path in sorted(drafts_dir.glob("*.yaml")):
        with open(draft_path, "r", encoding="utf-8") as f:
            draft_data = yaml.safe_load(f) or {}

        if "_meta" in draft_data:
            if args.dry_run:
                cleared_meta += 1
            else:
                del draft_data["_meta"]
                write_yaml(draft_path, draft_data)
                cleared_meta += 1

    console.print(f"\n[bold]Done![/bold]")
    console.print(f"  Moved to drafts: {moved}")
    console.print(f"  Kept in contents: {skipped}")
    if cleared_meta:
        console.print(f"  Cleared _meta from drafts: {cleared_meta}")


if __name__ == "__main__":
    main()
