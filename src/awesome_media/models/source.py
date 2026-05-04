import fastfeedparser
from rich.console import Console
from awesome_media.config import REQUIRED_FIELDS, ALLOWED_TAGS
from awesome_media.utils.strings import url_to_filename

console = Console()


def _normalize_rss_feeds(raw_rss):
    """
    Normalize rss_feed value into a list of {'url': str, 'label': str|None} dicts.
    Supports:
      - single string: "https://..."
      - list of strings: ["https://...", "https://..."]
      - list of dicts: [{"url": "...", "label": "..."}]
    """
    if not raw_rss:
        return []

    if isinstance(raw_rss, str):
        return [{"url": raw_rss, "label": None}]

    if isinstance(raw_rss, list):
        feeds = []
        for item in raw_rss:
            if isinstance(item, str):
                feeds.append({"url": item, "label": None})
            elif isinstance(item, dict):
                url = item.get("url", "")
                if url:
                    feeds.append({"url": url, "label": item.get("label")})
        return feeds

    return []


class Source:
    def __init__(self, filepath, data, validate_rss=False):
        self.filepath = filepath
        self.raw_data = data
        self._errors = []

        # 1. Normalize Fields
        self.title = str(data.get("title", ""))
        self.category = str(data.get("category", ""))
        self.media_type = str(data.get("media_type", self.category))
        self.country = str(data.get("country", ""))
        self.language = str(data.get("language", ""))
        self.description = str(data.get("description", ""))

        # 2. Normalize Website
        web = data.get("website")
        if isinstance(web, str):
            self.website_url = web
            self.website_text = "Visit Website"
        elif isinstance(web, dict):
            self.website_url = web.get("url", "")
            self.website_text = web.get("text", "Visit Website")
        else:
            self.website_url = ""
            self.website_text = "N/A"

        # 3. Normalize RSS (polymorphic: str, list of str, or list of dicts)
        raw_rss = data.get("rss_feed") or data.get("rss")
        self.rss_feeds = _normalize_rss_feeds(raw_rss)
        # Backward-compatible single URL
        self.rss_url = self.rss_feeds[0]["url"] if self.rss_feeds else ""

        # 4. Validate RSS Links (Only if explicitly requested)
        if validate_rss and self.rss_feeds:
            self._validate_rss()

        # 5. Normalize Tags
        raw_tags = data.get("tags", [])
        self.tags = sorted(list({str(t).strip().lower() for t in raw_tags if t}))

    def _comment_rss_in_file(self):
        """
        Opens the YAML file on disk and comments out the invalid rss_feed line.
        Only works for single-string rss_feed values.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            changed = False

            for line in lines:
                stripped = line.lstrip()
                if (
                    stripped.startswith("rss_feed:") or stripped.startswith("rss:")
                ) and not stripped.startswith("#"):
                    new_lines.append("#" + line)
                    changed = True
                else:
                    new_lines.append(line)

            if changed:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                console.print(
                    f"[dim]✎[/dim] Commented out invalid RSS in {self.filepath.name}"
                )

        except Exception as e:
            console.print(f"[red]Error updating file {self.filepath.name}: {e}[/red]")

    def _check_feed(self, url):
        """Returns True if the RSS URL is valid."""
        try:
            feed = fastfeedparser.parse(url)
            return bool(feed and feed.feed)
        except Exception:
            return False

    def _validate_rss(self):
        """
        Validates all RSS feeds.
        - For a single-string rss_feed, comments it out in the file if invalid.
        - For list-based rss_feeds, filters invalid ones in memory and warns.
        """
        raw_rss = self.raw_data.get("rss_feed") or self.raw_data.get("rss")
        is_single_string = isinstance(raw_rss, str)

        valid_feeds = []

        for feed_info in self.rss_feeds:
            url = feed_info["url"]
            label = feed_info["label"]
            if self._check_feed(url):
                valid_feeds.append(feed_info)
            else:
                display = f"{label} ({url})" if label else url
                console.print(
                    f"[yellow]RSS Warning:[/yellow] Invalid feed for [bold]{self.title}[/bold]: "
                    f"{display}"
                )
                # For single-string feeds, comment out the line in the file
                if is_single_string:
                    self._comment_rss_in_file()

        self.rss_feeds = valid_feeds
        self.rss_url = self.rss_feeds[0]["url"] if self.rss_feeds else ""

    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "media_type": self.media_type,
            "country": self.country,
            "language": self.language,
            "description": self.description,
            "website_url": self.website_url,
            "website_text": self.website_text,
            "rss_url": self.rss_url,
            "rss_feeds": self.rss_feeds,
            "tags": self.tags,
        }

    @property
    def expected_filename(self):
        if not self.website_url:
            return None
        return url_to_filename(self.website_url)

    def validate(self):
        """Validates fields and tags. Returns True if valid."""
        # A. Check Required Fields
        missing = [f for f in REQUIRED_FIELDS if f not in self.raw_data]
        if missing:
            self._errors.append(f"Missing fields: {missing}")

        # B. Check Filename Consistency
        if self.expected_filename and self.filepath.name != self.expected_filename:
            self._errors.append(
                f"Filename mismatch! File is '{self.filepath.name}' "
                f"but URL suggests '{self.expected_filename}'"
            )

        # C. Validate Tags
        invalid_tags = [t for t in self.tags if t not in ALLOWED_TAGS]
        if invalid_tags:
            self._errors.append(
                f"Invalid tags found: {invalid_tags}. "
                f"Please use tags from the generic list."
            )

        return len(self._errors) == 0

    def get_errors(self):
        return self._errors
