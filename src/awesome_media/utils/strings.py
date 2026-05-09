from urllib.parse import urlparse


def url_to_filename(url: str) -> str | None:
    """
    Converts a website URL to the expected YAML filename format.
    Returns None if the URL is empty or invalid.

    Examples:
        https://gunaz.tv/fa -> gunaz.tv.fa.yaml
        https://www.dw.com/fa-ir/ -> dw.com.fa-ir.yaml
    """
    if not url or not str(url).strip():
        return None

    try:
        parsed = urlparse(str(url).strip())
        # Remove 'www.' and convert to lowercase
        netloc = parsed.netloc.replace("www.", "").lower()

        if not netloc:
            return None

        # Remove leading/trailing slashes from path and replace internal ones with dots
        path = parsed.path.strip("/").replace("/", ".")

        # Combine
        if path:
            filename = f"{netloc}.{path}.yaml"
        else:
            filename = f"{netloc}.yaml"

        return filename
    except Exception:
        return None


def truncate_text(text: str, length: int = 120) -> str:
    if not text:
        return ""
    clean = text.replace("\n", " ").strip()
    return clean[:length] + "..." if len(clean) > length else clean
