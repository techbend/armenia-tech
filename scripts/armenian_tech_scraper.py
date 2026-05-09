#!/usr/bin/env python3
"""
Scrape Armenian tech companies from a Trello board HTML export
and generate content YAML files.

Usage:
    uv run python scripts/armenian_tech_scraper.py

The script reads scripts/board.html, extracts company cards from each list,
and writes YAML files.

- Cards with all labels (origin, employees, company_type) go to contents/.
- Cards missing labels go to drafts/ so they can be completed manually.

After filling in website URLs, run `make fix-names` to rename files to
match the url_to_filename() convention.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bs4 import BeautifulSoup
from rich.console import Console

from awesome_media.config import CONTENT_DIR

console = Console()

# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------
LIST_TO_TAG = {
    "cybersecurity": "cybersecurity",
    "developer tools / cloud": "developer-tools-cloud",
    "e-commerce / marketing / adtech": "e-commerce-marketing-adtech",
    "fintech / blockchain": "fintech-blockchain",
    "gambling": "gambling",
    "gamedev / ar / vr": "gamedev-ar-vr",
    "hardware / eda": "hardware-eda",
    "healthtech": "healthtech",
    "hr tech / edtech": "hr-tech-edtech",
    "lifetime / on demand / hospitality": "lifetime-on-demand-hospitality",
    "media / photo / video / audio / voip": "media-photo-video-audio-voip",
    "other product companies": "other-product-companies",
    "service providers": "service-providers",
}

VALID_ORIGINS = {"local", "global"}
VALID_EMPLOYEES = {"1-10", "11-50", "51-100", "101-250", "251-500", "500+"}
VALID_TYPES = {"service", "product"}


def slugify(name: str) -> str:
    """Create a filesystem-safe slug from a company name."""
    s = name.lower()
    s = re.sub(r"[^a-z0-9\s.-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = s.strip("-.")
    return s or "unknown"


def normalize_employees(val: str) -> str:
    """Convert Trello label to canonical form."""
    val = val.strip()
    if val == "500+":
        return "+500"
    return val


def build_yaml(
    name: str,
    origin: str | None,
    employees: str | None,
    company_type: str | None,
    tag: str,
) -> str:
    """Build a YAML string for a company."""
    def fmt(val: str | None) -> str:
        if val is None:
            return '""  # TODO'
        return f'"{val}"'

    lines = [
        f"name: {fmt(name)}",
        f"origin: {fmt(origin)}",
        f"employees: {fmt(employees)}",
        f"company_type: {fmt(company_type)}",
        "website:",
        '  url: ""  # TODO: add company website',
        'description: ""  # TODO: add description',
        "tags:",
        f"  - {tag}",
    ]
    return "\n".join(lines) + "\n"


def main():
    board_path = Path(__file__).resolve().parent / "board.html"
    if not board_path.exists():
        console.print(f"[red]Error:[/red] {board_path} not found.")
        sys.exit(1)

    with open(board_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    lists = soup.find_all("li", {"data-testid": "list-wrapper"})
    console.print(f"Found {len(lists)} lists in board.html")

    drafts_dir = Path(__file__).resolve().parent.parent / "drafts"
    drafts_dir.mkdir(exist_ok=True)

    # Track existing company names to avoid duplicates
    existing_names = {f.stem.lower() for f in CONTENT_DIR.glob("*.yaml")}
    draft_names = {f.stem.lower() for f in drafts_dir.glob("*.yaml")}

    created_content = 0
    created_drafts = 0
    skipped_content = 0
    skipped_draft = 0
    skipped_unknown_list = 0

    for lst in lists:
        list_name_elem = lst.find("h2", {"data-testid": "list-name"})
        if not list_name_elem:
            continue

        list_name = " ".join(list_name_elem.get_text().split()).lower()
        if list_name == "welcome":
            continue

        tag = LIST_TO_TAG.get(list_name)
        if not tag:
            console.print(f"[yellow]Warning:[/yellow] Unknown list '{list_name}' — skipping.")
            skipped_unknown_list += 1
            continue

        cards = lst.find_all("li", {"data-testid": "list-card"})
        for card in cards:
            name_elem = card.find("a", {"data-testid": "card-name"})
            if not name_elem:
                continue

            company_name = " ".join(name_elem.get_text().split())
            if not company_name:
                continue

            slug = slugify(company_name)

            # Extract labels (only present on fully-rendered cards)
            labels = [
                lbl.get_text(strip=True)
                for lbl in card.find_all("button", {"data-testid": "compact-card-label"})
            ]

            origins = [l for l in labels if l in VALID_ORIGINS]
            emps = [l for l in labels if l in VALID_EMPLOYEES]
            types = [l for l in labels if l in VALID_TYPES]

            origin = origins[0] if origins else None
            employees = normalize_employees(emps[0]) if emps else None
            company_type = types[0] if types else None

            yaml_text = build_yaml(company_name, origin, employees, company_type, tag)

            is_complete = origin is not None and employees is not None and company_type is not None

            if is_complete:
                target_path = CONTENT_DIR / f"{slug}.yaml"
                if target_path.exists() or slug in existing_names:
                    skipped_content += 1
                    continue
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(yaml_text)
                existing_names.add(slug)
                created_content += 1
            else:
                target_path = drafts_dir / f"{slug}.yaml"
                if target_path.exists() or slug in draft_names:
                    skipped_draft += 1
                    continue
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(yaml_text)
                draft_names.add(slug)
                created_drafts += 1

    console.print(f"\n[bold]Done![/bold]")
    console.print(f"  Written to contents/:  {created_content} (complete labels)")
    console.print(f"  Written to drafts/:    {created_drafts} (incomplete — needs manual work)")
    console.print(f"  Skipped (contents):    {skipped_content}")
    console.print(f"  Skipped (drafts):      {skipped_draft}")
    console.print(f"  Unknown lists:         {skipped_unknown_list}")
    console.print(
        "\n[bold]Next steps:[/bold]\n"
        "  1. Review files in [cyan]drafts/[/cyan] and move completed ones to [cyan]contents/[/cyan].\n"
        "  2. Add website URLs, then run [cyan]make fix-names[/cyan] to rename files.\n"
        "  3. Run [cyan]make build[/cyan] to validate and generate exports."
    )


if __name__ == "__main__":
    main()
