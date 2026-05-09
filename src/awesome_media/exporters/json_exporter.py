import json
from awesome_media.exporters.base import BaseExporter, console


class JsonExporter(BaseExporter):
    def export(self, companies):
        path = self.output_dir / "data.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                [self._serialize(c) for c in companies], f, indent=2, ensure_ascii=False
            )
        console.print(f"[green]✓[/green] Exported {len(companies)} companies to data.json")

    def _serialize(self, company):
        return {
            "name": company.name,
            "origin": company.origin,
            "employees": company.employees,
            "company_type": company.company_type,
            "description": company.description,
            "website_url": company.website_url,
            "website_text": company.website_text,
            "links": company.links,
            "tags": company.tags,
        }
