from rich.console import Console
from rich.table import Table
from rich import print as rprint

from awesome_media.config import OUTPUT_DIR
from awesome_media.loaders.yaml_loader import YamlLoader
from awesome_media.exporters.json_exporter import JsonExporter
from awesome_media.exporters.opml_exporter import OpmlExporter
from awesome_media.exporters.md_exporter import MarkdownExporter
# HTML export is now handled by the Svelte frontend build

console = Console()


def show_summary(sources):
    table = Table(title="Generated Summary")
    table.add_column("Source", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Country", style="yellow")
    table.add_column("Filename Check", justify="center")

    for entry in sources[:5]:
        feed_count = len(entry.rss_feeds)
        rss = f"✅ {feed_count}" if feed_count > 0 else "❌"
        c = (entry.country[:15] + "...") if len(entry.country) > 15 else entry.country
        table.add_row(entry.title, entry.media_type, c or "-", rss)

    if len(sources) > 5:
        table.add_row(f"... and {len(sources) - 5} more", "", "", "")
    console.print(table)


def main():
    rprint("[bold blue]Building Awesome Media...[/bold blue]")

    # 1. Load
    loader = YamlLoader()
    sources = loader.load()

    if not sources:
        console.print("[red]Abort:[/red] No sources found.")
        return

    total_feeds = sum(len(s.rss_feeds) for s in sources)
    console.print(f"[green]Found[/green] {len(sources)} media sources with {total_feeds} RSS feeds.\n")

    # 2. Summary
    show_summary(sources)
    print()

    # 3. Export
    # We inject OUTPUT_DIR to exporters
    JsonExporter(OUTPUT_DIR).export(sources)
    OpmlExporter(OUTPUT_DIR).export(sources)
    MarkdownExporter(OUTPUT_DIR).export(sources)
    # HTML site is built by the Svelte frontend (see frontend/ directory)

    rprint("\n[bold green]Build Complete![/bold green]")


if __name__ == "__main__":
    main()
