from pathlib import Path

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = ROOT_DIR / "contents"
OUTPUT_DIR = ROOT_DIR / "output"
README_PATH = ROOT_DIR / "index.md"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# --- Validation Rules ---
REQUIRED_FIELDS = ["name", "origin", "employees", "company_type", "website"]

ALLOWED_ORIGINS = ["local", "global"]
ALLOWED_EMPLOYEE_RANGES = ["1-10", "11-50", "51-100", "101-250", "251-500", "+500"]
ALLOWED_COMPANY_TYPES = ["service", "product"]

LINK_TYPES = ["linkedin", "careers", "twitter", "github", "facebook", "instagram", "youtube", "other"]

# Tech verticals / tags
ALLOWED_TAGS = [
    "cybersecurity",
    "developer-tools-cloud",
    "e-commerce-marketing-adtech",
    "fintech-blockchain",
    "gambling",
    "gamedev-ar-vr",
    "hardware-eda",
    "healthtech",
    "hr-tech-edtech",
    "lifetime-on-demand-hospitality",
    "media-photo-video-audio-voip",
    "other-product-companies",
    "service-providers",
]
