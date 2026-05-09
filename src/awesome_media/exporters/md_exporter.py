from awesome_media.exporters.base import BaseExporter, console
from awesome_media.config import README_PATH
from awesome_media.utils.strings import truncate_text


class MarkdownExporter(BaseExporter):
    def export(self, companies):
        header = """# Armenia Tech Landscape

A curated directory of Armenian tech companies — from local startups to global giants.

## 🏢 Companies

| Name | Origin | Employees | Type | Links | Tags | Description |
|------|--------|-----------|------|---------|------|-------------|
"""
        rows = []
        for c in companies:
            origin = ", ".join(c.origin) if c.origin else "-"
            ctype = ", ".join(c.company_type) if c.company_type else "-"
            tags = ", ".join(c.tags) if c.tags else "-"
            desc = truncate_text(c.description, 120)

            link_parts = []
            if c.website_url:
                link_parts.append(f"[{c.website_text}]({c.website_url})")
            for link in c.links:
                if link["url"]:
                    link_parts.append(f"[{link['type']}]({link['url']})")
            links_md = ", ".join(link_parts) if link_parts else "-"

            row = f"| {c.name} | {origin} | {c.employees} | {ctype} | {links_md} | {tags} | {desc} |\n"
            rows.append(row)

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(header + "".join(rows))

        console.print("[bold green]✓[/bold green] index.md generated")
