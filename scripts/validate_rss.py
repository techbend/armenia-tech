import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from awesome_media.loaders.yaml_loader import YamlLoader
from rich.console import Console

console = Console()


def main():
    rprint = console.print
    rprint("[bold blue]Validating RSS Feeds...[/bold blue]")
    rprint("This may take a while if you have many sources.\n")

    # Load sources with validation enabled
    loader = YamlLoader()
    sources = loader.load(validate_rss=True)

    # Summary
    total = len(sources)
    total_feeds = sum(len(s.rss_feeds) for s in sources)
    sources_with_feeds = len([s for s in sources if s.rss_feeds])

    console.print("\n[bold green]Validation Complete![/bold green]")
    console.print(f"Processed {total} valid sources.")
    console.print(f"Active RSS feeds: {total_feeds}")
    console.print(f"Sources with RSS: {sources_with_feeds}")
    console.print(f"Sources without RSS: {total - sources_with_feeds}")
    console.print(
        "\nInvalid single-feed links have been commented out in their respective YAML files."
    )
    console.print(
        "Invalid list-feed entries were filtered in memory (YAML files not modified)."
    )


if __name__ == "__main__":
    main()
