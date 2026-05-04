# Awesome Media Catalog — Agent Guide

## Project Overview
A curated catalog of trusted news outlets, podcasts, YouTube channels, newsletters, and independent sources. It uses an Object-Oriented Python architecture to validate YAML content, enforce naming conventions, and generate multiple export formats (HTML, Markdown, JSON, OPML) from a single source of truth.

**Live site:** https://tavallaie.github.io/awesome_media/

## Architecture

```
src/awesome_media/
├── main.py              # Entry point: load -> summarize -> export
├── config.py            # Paths, REQUIRED_FIELDS, ALLOWED_TAGS whitelist
├── loaders/
│   └── yaml_loader.py   # Loads & validates all contents/*.yaml into Source objects
├── models/
│   └── source.py        # Source dataclass with validation logic
├── exporters/
│   ├── base.py          # Abstract BaseExporter
│   ├── md_exporter.py   # Generates index.md (GitHub preview)
│   ├── json_exporter.py # Generates data.json
│   └── opml_exporter.py # Generates feeds.opml
└── utils/
    └── strings.py       # url_to_filename(), truncate_text()

scripts/
├── rename_mismatched_files.py  # Auto-renames YAML files to match their URLs
├── validate_rss.py             # Network check: comments out invalid RSS feeds
└── rss_finder.py               # Utility to discover RSS feeds for a URL

frontend/                  # Svelte + DaisyUI SPA
├── src/
│   ├── App.svelte
│   ├── main.js
│   ├── app.css
│   ├── components/
│   │   ├── Card.svelte
│   │   └── FilterSidebar.svelte
│   └── lib/
│       └── utils.js
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json

contents/
└── *.yaml               # One file per media source
```

## Key Conventions & Rules

### 1. Filename Enforcement
**CRITICAL:** Every YAML filename must match its website URL exactly.
- Use `scripts/rename_mismatched_files.py` (or `make fix-names`) to auto-fix.
- Conversion logic in `utils/strings.py:url_to_filename()`:
  - Strip `https://` and `www.`
  - Replace path slashes with dots
  - Examples:
    - `https://gunaz.tv/fa` → `gunaz.tv.fa.yaml`
    - `https://www.dw.com/fa-ir/` → `dw.com.fa-ir.yaml`

### 2. Tag Whitelisting
Only tags listed in `config.py:ALLOWED_TAGS` are permitted. If a new tag is needed, add it to `ALLOWED_TAGS` **before** using it in a content file. Invalid tags cause the source to be skipped during build.

### 3. Required Fields
Every YAML file must contain: `title`, `category`, `country`, `language`, `website`.

### 4. YAML Schema
```yaml
title: "Source Name"
category: "News"          # or Podcast, YouTube, Newsletter, etc.
country: "United Kingdom"
language: "Persian"
website:
  url: "https://www.bbc.com/persian"
  text: "Visit Website"   # optional, defaults to "Visit Website"
media_type: "News Website" # optional, falls back to category
description: "Short description..."
rss_feed: "https://..."    # optional; single feed (backward compatible)
# OR multiple feeds with optional labels:
# rss_feed:
#   - url: "https://example.com/fa/rss/allnews"
#     label: "All News"
#   - url: "https://example.com/fa/rss/politics"
#     label: "Politics"
tags:
  - global
  - politics
  - united-kingdom
```

### 5. RSS Handling
- `make validate-rss` performs slow network checks.
  - **Single-string `rss_feed`:** invalid feeds are commented out in the YAML file.
  - **List-based `rss_feed`:** invalid entries are filtered in-memory and logged; the YAML file is **not** modified.
- Standard `make build` skips RSS validation for speed.
- Multiple feeds per source are supported. Each feed appears as a separate entry in OPML exports, and as a dropdown in the HTML interface.

## Build System

| Command | Description |
|---------|-------------|
| `make build` | Full build (fix-names → Python exports → Svelte build) |
| `make fix-names` | Rename YAML files to match URLs |
| `make validate-rss` | Network check & comment out broken RSS |
| `make serve` | Build + start local server at `localhost:8000` |
| `make clean` | Remove `output/` directory |

All commands run via `uv run` (Python 3.12+).

## Validation Flow
1. `YamlLoader.load()` iterates `contents/*.yaml`
2. Each file is parsed and passed to `Source(file, data)`
3. `Source.validate()` checks:
   - Required fields present
   - Filename matches URL (`expected_filename`)
   - All tags are in `ALLOWED_TAGS`
4. Invalid sources are skipped with a warning; valid sources are sorted by title

## Export Flow
`main.py` calls exporters in sequence:
1. `JsonExporter` → `output/data.json`
2. `OpmlExporter` → `output/feeds.opml`
3. `MarkdownExporter` → `index.md`

Then the Svelte frontend is built to `output/`:
- `pnpm run build` (in `frontend/`) → `output/index.html` + `output/assets/`
- The SPA fetches `data.json` at runtime and renders the interactive catalog

## CI/CD
- **Trigger:** Push to `main`
- **Workflow:** `.github/workflows/deploy.yml`
- **Steps:** `uv sync` → `make build` → commit `README.md` updates → deploy `output/` to `gh-pages` branch via `peaceiris/actions-gh-pages`

## Adding a New Source
1. Create a YAML file in `contents/` with the correct filename (run `make fix-names` if unsure)
2. Ensure all required fields are present and tags are whitelisted in `config.py`
3. Run `make build` to verify
4. Commit both the new content file and any `config.py` tag additions

## Adding a New Tag
1. Add the tag string to `ALLOWED_TAGS` in `src/awesome_media/config.py`
2. Then use it in YAML content files

## Frontend Development
The UI is a Svelte SPA using Tailwind CSS and DaisyUI.

```bash
cd frontend
pnpm install
pnpm run dev      # Dev server
pnpm run build    # Production build to ../output
```

## Adding a New Exporter
1. Create a class inheriting from `BaseExporter` in `exporters/`
2. Implement `export(self, sources)`
3. Register it in `main.py`

## Technology Stack
- Python 3.12+
- `uv` for dependency management
- `jinja2` for HTML templating
- `pyyaml` for content parsing
- `rich` for CLI output
- `fastfeedparser` for RSS validation
- `beautifulsoup4` / `lxml` / `requests` for utilities
