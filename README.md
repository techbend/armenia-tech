# Armenia Tech Landscape

A curated directory of Armenian tech companies — from Yerevan-based startups to globally successful enterprises founded by Armenians.

## 🌐 Live Site

Visit the interactive catalog: **[Armenia Tech Landscape](https://tavallaie.github.io/armenia-tech-landscape/)**

## 📋 About

This project maps the Armenian tech ecosystem, covering companies across sectors like:

- **AI & Machine Learning**
- **Cybersecurity**
- **Developer Tools & Cloud**
- **Fintech**
- **SaaS & Enterprise Software**
- **HealthTech, EdTech, and more**

Each company is tagged by:
- **Origin**: Local (based in Armenia) or Global (founded by Armenians abroad)
- **Size**: Employee count ranges
- **Type**: Product or Service company
- **Verticals**: Tech sector tags

## 🏢 Companies

See the full catalog in the [live site](https://tavallaie.github.io/armenia-tech-landscape/) or browse [`contents/`](./contents/) for the raw YAML data.

## 🛠️ Contributing

### Adding a Company

1. Create a YAML file in `contents/` named after the company's website URL:
   - `https://example.com` → `example.com.yaml`
   - Run `make fix-names` to auto-correct filenames

2. Use this schema:
   ```yaml
   name: "Company Name"
   origin: "local"          # or "global"
   employees: "11-50"       # 1-10 | 11-50 | 51-100 | 101-250 | 251-500 | +500
   company_type: "product"  # or "service"
   website:
     url: "https://example.com"
   links:
     - url: "https://linkedin.com/company/example"
       type: "linkedin"
     - url: "https://example.com/careers"
       type: "careers"
   description: "What the company does..."
   tags:
     - saas
     - ai-ml
   ```

   **Link types:** `linkedin`, `careers`, `twitter`, `github`, `facebook`, `instagram`, `youtube`, `other`

3. Tags must be from the allowed list in `src/awesome_media/config.py`. Add new tags there first if needed.

4. Run `make build` to verify and preview locally.

### Development Setup

```bash
# Install Python dependencies
uv sync

# Build everything
make build

# Serve locally
make serve

# Frontend only
cd frontend
pnpm install
pnpm run dev
```

## 🤖 Automation Scripts

All scripts run via `uv run python scripts/<script>.py`.

### Scrape from Trello board HTML

```bash
uv run python scripts/armenian_tech_scraper.py
```

Reads `scripts/board.html` (a saved Trello board export) and generates YAML files:
- **Complete cards** (with origin / employees / company_type labels) → `contents/`
- **Incomplete cards** → `drafts/`

### Find incomplete YAMLs

```bash
# Console report
uv run python scripts/find_incomplete_yamls.py

# JSON report
uv run python scripts/find_incomplete_yamls.py --json report.json

# Only drafts
uv run python scripts/find_incomplete_yamls.py --only-drafts
```

Shows which fields are missing per file and distinguishes **Checked** vs **Unchecked**.

### Auto-complete with Gemini (+ Google Search)

```bash
# 1. Set your key
cp .env.example .env
# edit .env and add GEMINI_API_KEY

# 2. Run (batches 20 companies per API call by default)
uv run python scripts/complete_yamls_with_gemini.py

# Process only 50, with 3s delay between batches
uv run python scripts/complete_yamls_with_gemini.py --limit 50 --delay 3

# Preview prompts without calling API
uv run python scripts/complete_yamls_with_gemini.py --preview --limit 30

# Save prompts to JSON for manual use
uv run python scripts/complete_yamls_with_gemini.py --save-prompts prompts.json

# Re-check files that were already processed
uv run python scripts/complete_yamls_with_gemini.py --recheck
```

**Features:**
- Batching (default 20 per call)
- Google Search grounding
- Model set via `GEMINI_MODEL` env var (default: `gemini-3.1-flash-lite`)
- Auto-retry with exponential backoff on rate limits
- Resumable via `.gemini_progress.json`
- Skips already-checked files unless `--recheck` is passed

### Apply manual LLM output

If you ran the prompts elsewhere and have the JSON responses:

```bash
uv run python scripts/apply_llm_output.py --input responses.json

# Dry run first
uv run python scripts/apply_llm_output.py --input responses.json --dry-run

# Also improve existing contents/ files
uv run python scripts/apply_llm_output.py --input responses.json --include-contents
```

Accepts a JSON array (or object with `results`/`companies`/`data`/`items` key) where each element has an `index` matching the file order.

### Fix filenames

```bash
make fix-names
```

Renames YAML files to match their `website.url` using the `url_to_filename()` convention.

## 📁 Project Structure

- `contents/` — Company data (one YAML file per company)
- `drafts/` — Incomplete YAMLs waiting for manual or LLM completion
- `src/awesome_media/` — Python backend for validation and export
- `frontend/` — Svelte SPA for the interactive web UI
- `output/` — Generated site (HTML, JSON, assets)
- `scripts/` — Automation tools (scraper, LLM completion, etc.)

## 📄 License

MIT
