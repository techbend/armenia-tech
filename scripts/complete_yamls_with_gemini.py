#!/usr/bin/env python3
"""
Use Google Gemini (with Search + batching) to complete missing fields in YAML drafts.

Usage:
    export GEMINI_API_KEY="your-key"
    uv run python scripts/complete_yamls_with_gemini.py
    uv run python scripts/complete_yamls_with_gemini.py --limit 100 --batch-size 20 --delay 2

Features:
- Batching: sends N companies per API call (default 20)
- Google Search grounding: lets Gemini browse the web for current info
- Single model (you pick it via --model or GEMINI_MODEL env var)
- Auto-retry with exponential backoff on rate-limit errors
- Resumable via .gemini_progress.json
- Match by filename (never shifts)
"""

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import requests
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from awesome_media.config import (
    ALLOWED_ORIGINS,
    ALLOWED_EMPLOYEE_RANGES,
    ALLOWED_COMPANY_TYPES,
    CONTENT_DIR,
)
from awesome_media.utils.strings import url_to_filename

console = Console()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

PROGRESS_FILE = Path(".gemini_progress.json")


def _api_call(prompt: str, model: str, api_key: str) -> dict:
    """Make a single Gemini API call with Google Search enabled."""
    url = GEMINI_API_URL.format(model=model)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }
    resp = requests.post(
        url,
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def gemini_request(prompt: str, model: str, api_key: str, max_retries: int = 5) -> dict:
    """Call Gemini with exponential backoff on rate limits."""
    last_error = None
    for attempt in range(max_retries):
        try:
            data = _api_call(prompt, model, api_key)
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in response")
            text = candidates[0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status in (429, 503, 504):
                sleep = (2 ** attempt) + random.uniform(0, 1)
                console.print(
                    f"[yellow]Rate limit ({status}) on {model}, retry in {sleep:.1f}s...[/yellow]"
                )
                time.sleep(sleep)
                last_error = e
                continue
            raise
        except Exception as e:
            raise

    raise last_error or RuntimeError(f"Model {model} failed after {max_retries} retries")


def build_batch_prompt(batch: list) -> str:
    """Build a single prompt for a batch of companies."""
    lines = [
        "You are a tech-industry research assistant with Google Search access.",
        "Find accurate public information about each company below.",
        "",
        'Return ONLY a JSON array. Each element MUST have this exact shape (no markdown, no explanation):',
        "[",
        '  {',
        '    "filename": "exact-yaml-filename.yaml",',
        '    "name": "Exact company name",',
        '    "website_url": "https://..." or null,',
        '    "linkedin_url": "https://www.linkedin.com/company/..." or null,',
        '    "careers_url": "https://.../careers" or null,',
        '    "description": "One clear sentence (max 200 chars)." or null,',
        '    "origin": "local" or "global" or null,',
        '    "employees": "1-10" or "11-50" or "51-100" or "101-250" or "251-500" or "+500" or null,',
        '    "company_type": "product" or "service" or null',
        '  }',
        "]",
        "",
        "Rules:",
        '- "local" = Armenian-founded or HQ in Armenia.',
        '- "global" = International company with Armenian operations.',
        '- If uncertain, use null. Never guess.',
        "",
        "Companies:",
    ]

    for item in batch:
        name = item["name"]
        tag = item["tag"]
        filename = item["path"].name
        known = []
        for k in ["origin", "employees", "company_type", "description"]:
            v = item["data"].get(k)
            if v and str(v).strip() and not str(v).strip().startswith("# TODO"):
                known.append(f"{k}={v}")
        known_str = ", ".join(known) if known else "nothing known"
        lines.append(f"filename: {filename}")
        lines.append(f"name: {name}")
        lines.append(f"tag: {tag}")
        lines.append(f"known: {known_str}")
        lines.append("")

    return "\n".join(lines)


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


def update_yaml(path: Path, gemini_result: dict) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    web = sanitize_url(gemini_result.get("website_url"))
    if web:
        if isinstance(data.get("website"), dict):
            data["website"]["url"] = web
        else:
            data["website"] = {"url": web}

    li = sanitize_url(gemini_result.get("linkedin_url"))
    if li:
        links = data.get("links", [])
        if not isinstance(links, list):
            links = []
        has_li = any(isinstance(l, dict) and l.get("type") == "linkedin" for l in links)
        if not has_li:
            links.append({"url": li, "type": "linkedin"})
        data["links"] = links

    careers = sanitize_url(gemini_result.get("careers_url"))
    if careers:
        links = data.get("links", [])
        if not isinstance(links, list):
            links = []
        has_careers = any(isinstance(l, dict) and l.get("type") == "careers" for l in links)
        if not has_careers:
            links.append({"url": careers, "type": "careers"})
        data["links"] = links

    desc = gemini_result.get("description")
    if desc and str(desc).strip().lower() not in ("null", "none", "n/a", ""):
        data["description"] = str(desc).strip()

    origin = sanitize_choice(gemini_result.get("origin"), set(ALLOWED_ORIGINS))
    if origin:
        data["origin"] = origin

    employees = sanitize_choice(gemini_result.get("employees"), set(ALLOWED_EMPLOYEE_RANGES))
    if employees:
        data["employees"] = employees

    ctype = sanitize_choice(gemini_result.get("company_type"), set(ALLOWED_COMPANY_TYPES))
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


def is_complete(data: dict) -> bool:
    for field in ["name", "origin", "employees", "company_type"]:
        v = data.get(field)
        if not v or not str(v).strip() or str(v).strip().startswith("# TODO"):
            return False
    web = data.get("website")
    url = web.get("url", "") if isinstance(web, dict) else (web or "")
    if not url or not url.strip() or url.strip().startswith("# TODO"):
        return False
    return True


def load_progress() -> set:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_progress(processed: set) -> None:
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(processed), f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Complete YAML drafts with Gemini + Search")
    parser.add_argument("--limit", type=int, default=0, help="Max files to process (0 = unlimited)")
    parser.add_argument("--batch-size", type=int, default=20, help="Companies per API call")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between API calls")
    parser.add_argument("--drafts-dir", type=str, default="drafts", help="Drafts directory")
    parser.add_argument("--contents-dir", type=str, default="contents", help="Contents directory")
    parser.add_argument("--include-contents", action="store_true", help="Also scan contents/ for incomplete files")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    parser.add_argument("--max-retries", type=int, default=5, help="Max retries per API call")
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help="Gemini model name (default: GEMINI_MODEL env var or gemini-3.1-flash-lite)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print prompts to stdout instead of calling the API",
    )
    parser.add_argument(
        "--save-prompts",
        type=str,
        metavar="FILE",
        help="Save all batch prompts to a JSON file for manual use",
    )
    parser.add_argument(
        "--recheck",
        action="store_true",
        help="Re-check files that already have _meta.checked_at",
    )
    args = parser.parse_args()

    if not args.preview and not GEMINI_API_KEY:
        console.print("[red]Error:[/red] Set GEMINI_API_KEY environment variable.")
        sys.exit(1)

    root = Path(__file__).resolve().parent.parent
    drafts_dir = root / args.drafts_dir
    contents_dir = root / args.contents_dir

    files = []
    if drafts_dir.exists():
        files.extend(sorted(drafts_dir.glob("*.yaml")))
    if args.include_contents and contents_dir.exists():
        files.extend(sorted(contents_dir.glob("*.yaml")))

    if not files:
        console.print("[yellow]No YAML files found.[/yellow]")
        sys.exit(0)

    processed = load_progress()
    files = [f for f in files if str(f) not in processed]

    if not args.recheck:
        before = len(files)
        files = [f for f in files if not is_checked(f)]
        skipped_checked = before - len(files)
        if skipped_checked:
            console.print(f"[yellow]Skipping {skipped_checked} already-checked files (use --recheck to override).[/yellow]")

    if args.limit > 0:
        files = files[: args.limit]

    # Build work items
    items = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        items.append(
            {
                "path": path,
                "name": data.get("name", path.stem),
                "tag": data.get("tags", ["unknown"])[0]
                if data.get("tags")
                else "unknown",
                "data": data,
            }
        )

    console.print(f"Processing {len(items)} files in batches of {args.batch_size}...")

    updated = 0
    moved = 0
    failed = 0
    api_calls = 0
    saved_prompts = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=len(items))

        for batch_start in range(0, len(items), args.batch_size):
            batch = items[batch_start : batch_start + args.batch_size]
            progress.update(
                task,
                description=f"Batch {batch_start // args.batch_size + 1}/{(len(items) - 1) // args.batch_size + 1} ({len(batch)} items)...",
            )

            prompt = build_batch_prompt(batch)

            if args.preview or args.save_prompts:
                if args.preview:
                    console.print(f"\n[bold]=== Batch {batch_start // args.batch_size + 1} ===[/bold]")
                    console.print(prompt)
                    console.print("=" * 40)
                if args.save_prompts:
                    saved_prompts.append(
                        {
                            "batch": batch_start // args.batch_size + 1,
                            "items": [
                                {"filename": item["path"].name, "name": item["name"]}
                                for item in batch
                            ],
                            "prompt": prompt,
                        }
                    )
                continue

            try:
                results = gemini_request(prompt, args.model, GEMINI_API_KEY, args.max_retries)
                api_calls += 1

                # Normalize results to a list
                if isinstance(results, dict):
                    for key in ("results", "companies", "data", "items"):
                        if key in results:
                            results = results[key]
                            break
                    if isinstance(results, dict):
                        results = [results]
                if not isinstance(results, list):
                    console.print(f"[yellow]Unexpected response shape: {type(results).__name__}[/yellow]")
                    failed += len(batch)
                    continue

                # Map results by filename (primary) or index (fallback)
                result_map = {}
                for r in results:
                    fname = r.get("filename")
                    if fname:
                        result_map[fname] = r
                    else:
                        idx = r.get("index")
                        if idx is not None and 0 <= idx < len(batch):
                            result_map[batch[idx]["path"].name] = r

                for item in batch:
                    path = item["path"]
                    try:
                        result = result_map.get(path.name)
                        if not result:
                            console.print(f"[yellow]Missing result for {item['name']} ({path.name})[/yellow]")
                            failed += 1
                            continue

                        if args.dry_run:
                            console.print(f"[cyan]DRY[/cyan] {item['name']}: {result}")
                        else:
                            updated_data = update_yaml(path, result)
                            updated_data = mark_checked(updated_data)
                            write_yaml(path, updated_data)

                            # Move to contents/ if complete
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
                                    path = target
                                    moved += 1

                            updated += 1
                            processed.add(str(path))
                    except Exception as e:
                        console.print(f"[red]Failed {path.name}:[/red] {e}")
                        failed += 1

            except Exception as e:
                console.print(f"[red]Batch failed:[/red] {e}")
                failed += len(batch)

            progress.advance(task, advance=len(batch))
            save_progress(processed)

            if args.delay > 0 and batch_start + args.batch_size < len(items):
                time.sleep(args.delay)

    if args.save_prompts and saved_prompts:
        with open(args.save_prompts, "w", encoding="utf-8") as f:
            json.dump(saved_prompts, f, indent=2)
        console.print(f"[green]Saved {len(saved_prompts)} prompts to {args.save_prompts}[/green]")

    console.print(f"\n[bold]Done![/bold]")
    console.print(f"  API calls:     {api_calls}")
    console.print(f"  Updated:       {updated}")
    console.print(f"  Moved:         {moved}")
    console.print(f"  Failed:        {failed}")
    console.print(f"  Total items:   {len(items)}")


if __name__ == "__main__":
    main()
