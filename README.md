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
   description: "What the company does..."
   tags:
     - saas
     - ai-ml
   ```

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

## 📁 Project Structure

- `contents/` — Company data (one YAML file per company)
- `src/awesome_media/` — Python backend for validation and export
- `frontend/` — Svelte SPA for the interactive web UI
- `output/` — Generated site (HTML, JSON, assets)

## 📄 License

MIT
