# Armenia Tech Landscape — Agent Guide

## Project Overview
A curated directory of Armenian tech companies, from local startups to global giants. It uses an Object-Oriented Python architecture to validate YAML content, enforce naming conventions, and generate multiple export formats (HTML, Markdown, JSON) from a single source of truth.

**Live site:** https://tavallaie.github.io/armenia-tech-landscape/

## Architecture

```
src/awesome_media/
├── main.py              # Entry point: load → summarize → export
├── config.py            # Paths, REQUIRED_FIELDS, ALLOWED_TAGS whitelist
├── loaders/
│   └── yaml_loader.py   # Loads & validates all contents/*.yaml into Company objects
├── models/
│   └── company.py       # Company dataclass with validation logic
├── exporters/
│   ├── base.py          # Abstract BaseExporter
│   ├── json_exporter.py # Generates data.json
│   └── md_exporter.py   # Generates index.md (GitHub preview)
└── utils/
    └── strings.py       # url_to_filename(), truncate_text()

scripts/
└── rename_mismatched_files.py  # Auto-renames YAML files to match their URLs

frontend/                  # Svelte + DaisyUI SPA
├── src/
│   ├── App.svelte
│   ├── main.js
│   ├── app.css
│   ├── components/
│   │   ├── Card.svelte
│   │   ├── FilterSidebar.svelte
│   │   └── FilterSelect.svelte
│   └── lib/
│       └── utils.js
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json

contents/
└── *.yaml               # One file per company
```

## Key Conventions & Rules

### 1. Filename Enforcement
**CRITICAL:** Every YAML filename must match its website URL exactly.
- Use `scripts/rename_mismatched_files.py` (or `make fix-names`) to auto-fix.
- Conversion logic in `utils/strings.py:url_to_filename()`:
  - Strip `https://` and `www.`
  - Replace path slashes with dots
  - Examples:
    - `https://picsart.com` → `picsart.com.yaml`
    - `https://krisp.ai` → `krisp.ai.yaml`

### 2. Tag Whitelisting
Only tags listed in `config.py:ALLOWED_TAGS` are permitted. If a new tag is needed, add it to `ALLOWED_TAGS` **before** using it in a content file. Invalid tags cause the company to be skipped during build.

### 3. Required Fields
Every YAML file must contain: `name`, `origin`, `employees`, `company_type`, `website`.

### 4. YAML Schema
```yaml
name: "Company Name"
origin: "local"              # or "global"
employees: "11-50"           # one of: 1-10, 11-50, 51-100, 101-250, 251-500, +500
company_type: "product"      # or "service"
website:
  url: "https://example.com"
  text: "Visit Website"      # optional, defaults to "Visit Website"
description: "Short description..."
tags:
  - ai-ml
  - saas
```

## Build System

| Command | Description |
|---------|-------------|
| `make build` | Full build (fix-names → Python exports → Svelte build) |
| `make fix-names` | Rename YAML files to match URLs |
| `make serve` | Build + start local server at `localhost:8000` |
| `make clean` | Remove `output/` directory |

All commands run via `uv run` (Python 3.12+).

## Validation Flow
1. `YamlLoader.load()` iterates `contents/*.yaml`
2. Each file is parsed and passed to `Company(file, data)`
3. `Company.validate()` checks:
   - Required fields present
   - Filename matches URL (`expected_filename`)
   - All tags are in `ALLOWED_TAGS`
   - `origin` is in `ALLOWED_ORIGINS`
   - `employees` is in `ALLOWED_EMPLOYEE_RANGES`
   - `company_type` is in `ALLOWED_COMPANY_TYPES`
4. Invalid companies are skipped with a warning; valid companies are sorted by name

## Export Flow
`main.py` calls exporters in sequence:
1. `JsonExporter` → `output/data.json`
2. `MarkdownExporter` → `index.md`

Then the Svelte frontend is built to `output/`:
- `pnpm run build` (in `frontend/`) → `output/index.html` + `output/assets/`
- The SPA fetches `data.json` at runtime and renders the interactive catalog

## CI/CD
- **Trigger:** Push to `main`
- **Workflow:** `.github/workflows/deploy.yml`
- **Steps:** `uv sync` → `make build` → commit `README.md` updates → deploy `output/` to `gh-pages` branch via `peaceiris/actions-gh-pages`

## Adding a New Company
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
2. Implement `export(self, companies)`
3. Register it in `main.py`

## Technology Stack
- Python 3.12+
- `uv` for dependency management
- `jinja2` for HTML templating
- `pyyaml` for content parsing
- `rich` for CLI output
- `beautifulsoup4` / `lxml` / `requests` for utilities
