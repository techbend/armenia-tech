# 🌟 Awesome Media Catalog

A curated catalog of trusted news outlets, podcasts, YouTube channels, newsletters, and independent sources.

[![Live Site](https://img.shields.io/badge/Live-Website-green?style=for-the-badge&logo=github)](https://tavallaie.github.io/awesome_media/)
[![Build Status](https://img.shields.io/badge/Build-Automated-blue?style=for-the-badge&logo=github-actions)](https://github.com/tavallaie/awesome_media/actions)

## 🌐 Live Version

Visit the interactive catalog at: [https://tavallaie.github.io/awesome_media/](https://tavallaie.github.io/awesome_media/)

## 📖 About

This project provides a modern, filterable interface for discovering high-quality media resources. It uses a **Python backend** to validate content and generate data exports, and a **Svelte + DaisyUI frontend** to render a fast, interactive catalog.

## ✨ Features

* **Strict Content Validation**
    * **Filename Enforcement:** Filenames must match the website URL (e.g., `gunaz.tv/fa` → `gunaz.tv.fa.yaml`)
    * **Tag Whitelisting:** Only approved tags are permitted to prevent bloat
* **Multiple RSS Feeds per Source:** Sites with category-specific feeds are fully supported
* **Feed Selection:** Select individual RSS feeds and export a tailored OPML for your reader
* **Dynamic Filters:** Search, filter by category, type, country, language, and tags
* **Multiple Exports:**
    * **Interactive HTML (Svelte SPA):** Filterable card-grid with per-feed checkboxes
    * **Markdown (`index.md`):** Static table view for GitHub previews
    * **JSON & OPML:** Machine-readable data and RSS import files
* **Automated Workflow:** GitHub Actions builds and deploys on every push

## 🚀 Getting Started

### Prerequisites
* **Python 3.12+**
* **[uv](https://github.com/astral-sh/uv)** — Python package manager
* **Node.js 20+**
* **[pnpm](https://pnpm.io/)** — Node package manager

### Installation & Build

```bash
# Clone
git clone https://github.com/tavallaie/awesome_media.git
cd awesome_media

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && pnpm install && cd ..

# Full build (data + frontend)
make build

# Or run individual steps
make json        # Just regenerate data.json
make opml        # Just regenerate feeds.opml
make site        # Just build the Svelte frontend

# Serve locally
make serve       # http://localhost:8000
```

## 🗂️ Project Structure

```text
.
├── contents/                # YAML source files (single source of truth)
├── frontend/                # Svelte + DaisyUI SPA
│   ├── src/
│   │   ├── App.svelte
│   │   ├── components/
│   │   │   ├── Card.svelte
│   │   │   └── FilterSidebar.svelte
│   │   └── lib/
│   ├── index.html
│   └── package.json
├── scripts/                 # Utility scripts
│   ├── rename_mismatched_files.py
│   ├── validate_rss.py
│   └── rss_finder.py
├── src/                     # Python backend
│   └── awesome_media/
│       ├── main.py
│       ├── config.py        # ALLOWED_TAGS & validation rules
│       ├── models/
│       └── exporters/
└── output/                  # Generated static site (deployed to GitHub Pages)
```

## 📝 Adding a New Source

Create a `.yaml` file in `contents/`:

### 1. Naming Convention
The filename **must** match the URL:
* `https://www.dw.com/fa-ir/` → `dw.com.fa-ir.yaml`
* `https://iranintl.com` → `iranintl.com.yaml`

> Run `make fix-names` to auto-correct filenames.

### 2. Allowed Tags
Tags must exist in `src/awesome_media/config.py:ALLOWED_TAGS`.

### 3. YAML Template

```yaml
title: "Example News"
category: "News"
country: "Germany"
language: "Persian"
website:
  url: "https://example.com"
  text: "Visit Website"
media_type: "News Website"
description: "Brief description of the source."

# Single feed (backward compatible)
rss_feed: "https://example.com/feed.xml"

# Or multiple feeds with labels
# rss_feed:
#   - url: "https://example.com/fa/rss/allnews"
#     label: "All News"
#   - url: "https://example.com/fa/rss/politics"
#     label: "Politics"

tags:
  - iran
  - politics
  - global
```

## 🛠️ Makefile Targets

| Command | Description |
|---------|-------------|
| `make build` | Full pipeline: fix names → export data → build frontend |
| `make data` | Export JSON + OPML + Markdown (no frontend) |
| `make json` | Export `data.json` only |
| `make opml` | Export `feeds.opml` only |
| `make readme` | Export `index.md` only |
| `make site` | Build Svelte frontend only |
| `make fix-names` | Rename YAML files to match URLs |
| `make validate-rss` | Network check & comment out invalid RSS |
| `make rss-finder` | Discover RSS feeds for a URL |
| `make serve` | Build + start local server |
| `make clean` | Remove `output/` directory |

## 🤖 CI/CD

GitHub Actions workflow:
1. **On push to `main`:** Runs `make build`
2. **Commits:** Updates `index.md` back to `main`
3. **Deploys:** Pushes `output/` to the `gh-pages` branch

## 📜 License

MIT License
