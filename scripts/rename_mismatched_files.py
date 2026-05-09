import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import yaml
from rich.console import Console
from awesome_media.config import CONTENT_DIR
from awesome_media.utils.strings import url_to_filename

console = Console()


def main():
    if not CONTENT_DIR.exists():
        console.print("[red]Error:[/red] 'contents' directory not found.")
        return

    yaml_files = sorted(CONTENT_DIR.glob("*.yaml"))
    renamed = 0
    skipped = 0

    for file in yaml_files:
        if file.name.lower().startswith("example"):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                continue

            web = data.get("website")
            if isinstance(web, dict):
                url = web.get("url", "")
            else:
                url = web or ""

            if not url:
                console.print(f"[yellow]Skipping {file.name}:[/yellow] No website URL found.")
                skipped += 1
                continue

            expected = url_to_filename(url)
            if file.name != expected:
                target = file.parent / expected
                if target.exists():
                    console.print(
                        f"[yellow]Cannot rename {file.name} → {expected}:[/yellow] Target exists."
                    )
                    skipped += 1
                else:
                    file.rename(target)
                    console.print(f"[green]Renamed[/green] {file.name} → {expected}")
                    renamed += 1

        except Exception as e:
            console.print(f"[red]Error processing {file.name}:[/red] {e}")
            skipped += 1

    console.print(f"\n[bold]Done:[/bold] {renamed} renamed, {skipped} skipped.")


if __name__ == "__main__":
    main()
