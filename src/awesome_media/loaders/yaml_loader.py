import yaml
from rich.console import Console
from awesome_media.config import CONTENT_DIR
from awesome_media.models.company import Company

console = Console()


class YamlLoader:
    def load(self):
        companies = []
        if not CONTENT_DIR.exists():
            console.print("[red]Error:[/red] 'contents' directory not found.")
            return []

        yaml_files = sorted(CONTENT_DIR.glob("*.yaml"))

        for file in yaml_files:
            if file.name.lower().startswith("example"):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if not data:
                    continue

                company = Company(file, data)

                if company.validate():
                    companies.append(company)
                else:
                    console.print(
                        f"[yellow]Skipping {file.name}:[/yellow] {company.get_errors()}"
                    )

            except Exception as e:
                console.print(f"[red]Error loading {file.name}:[/red] {e}")

        return sorted(companies, key=lambda x: x.name.lower())
