from rich.console import Console
from rich.table import Table
from rich import print as rprint

from awesome_media.config import OUTPUT_DIR
from awesome_media.loaders.yaml_loader import YamlLoader
from awesome_media.exporters.json_exporter import JsonExporter
from awesome_media.exporters.md_exporter import MarkdownExporter

console = Console()


def show_summary(companies):
    table = Table(title="Generated Summary")
    table.add_column("Company", style="cyan")
    table.add_column("Origin", style="magenta")
    table.add_column("Employees", style="yellow")
    table.add_column("Type", style="green")

    for entry in companies[:5]:
        origin = ", ".join(entry.origin) if entry.origin else "-"
        ctype = ", ".join(entry.company_type) if entry.company_type else "-"
        table.add_row(entry.name, origin, entry.employees, ctype)

    if len(companies) > 5:
        table.add_row(f"... and {len(companies) - 5} more", "", "", "")
    console.print(table)


def main():
    rprint("[bold blue]Building Armenia Tech Landscape...[/bold blue]")

    # 1. Load
    loader = YamlLoader()
    companies = loader.load()

    if not companies:
        console.print("[red]Abort:[/red] No companies found.")
        return

    console.print(f"[green]Found[/green] {len(companies)} companies.\n")

    # 2. Summary
    show_summary(companies)
    print()

    # 3. Export
    JsonExporter(OUTPUT_DIR).export(companies)
    MarkdownExporter(OUTPUT_DIR).export(companies)

    rprint("\n[bold green]Build Complete![/bold green]")


if __name__ == "__main__":
    main()
