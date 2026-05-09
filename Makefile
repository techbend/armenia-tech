# =============================================
# Armenia Tech Landscape - Makefile
# =============================================

# Use 'uv run' to execute commands within the project environment
UV := uv run

# Export PYTHONPATH so Python can find the 'src' module
export PYTHONPATH := src

# Frontend build
FRONTEND_DIR := frontend
PNPM := pnpm

.PHONY: help build data json readme site serve clean fix-names

help:
	@echo "Available targets:"
	@echo ""
	@echo "  Quick Actions:"
	@echo "  ─────────────"
	@echo "  build           Full build: fix names → export data → build frontend"
	@echo "  data            Export JSON + Markdown (no frontend)"
	@echo "  json            Export data.json only"
	@echo "  readme          Export index.md only"
	@echo "  site            Build Svelte frontend only"
	@echo "  serve           Build + start local server at localhost:8000"
	@echo ""
	@echo "  Maintenance:"
	@echo "  ───────────"
	@echo "  fix-names       Rename YAML files to match their URLs"
	@echo "  clean           Remove output directory"

# ====================== Main Targets ======================

# Standard build: full pipeline
build: fix-names
	@mkdir -p output
	$(UV) python -m awesome_media.main
	@echo "Building Svelte frontend..."
	cd $(FRONTEND_DIR) && $(PNPM) install && $(PNPM) run build

# Export all data formats (JSON + Markdown)
data:
	@mkdir -p output
	$(UV) python -m awesome_media.main

# Export individual formats
json:
	@mkdir -p output
	$(UV) python -c "from awesome_media.config import OUTPUT_DIR; from awesome_media.loaders.yaml_loader import YamlLoader; from awesome_media.exporters.json_exporter import JsonExporter; JsonExporter(OUTPUT_DIR).export(YamlLoader().load())"

readme:
	$(UV) python -c "from awesome_media.config import OUTPUT_DIR; from awesome_media.loaders.yaml_loader import YamlLoader; from awesome_media.exporters.md_exporter import MarkdownExporter; MarkdownExporter(OUTPUT_DIR).export(YamlLoader().load())"

# Build frontend only (assumes data.json already exists)
site:
	@echo "Building Svelte frontend..."
	cd $(FRONTEND_DIR) && $(PNPM) install && $(PNPM) run build

# ====================== Maintenance ======================

fix-names:
	$(UV) python scripts/rename_mismatched_files.py

serve: build
	@echo "========================================"
	@echo "Site built successfully!"
	@echo "Starting local server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	@echo "========================================"
	cd output && $(UV) python -m http.server 8000

clean:
	rm -rf output
	@echo "✅ Cleaned output directory"

# ====================== Aliases ======================

all: build
run: serve
