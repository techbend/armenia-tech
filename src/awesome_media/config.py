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

# Tech verticals / tags
ALLOWED_TAGS = [
    "ai-ml",
    "ar-vr",
    "biotech",
    "blockchain",
    "cloud",
    "cybersecurity",
    "data-analytics",
    "design-creative",
    "developer-tools",
    "devops",
    "e-commerce",
    "edtech",
    "fintech",
    "gaming",
    "healthtech",
    "hr-tech",
    "iot",
    "logistics",
    "marketing-tech",
    "mobile-apps",
    "open-source",
    "robotics",
    "saas",
    "semiconductors",
    "web3",
]
