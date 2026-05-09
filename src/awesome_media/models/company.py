from awesome_media.config import (
    REQUIRED_FIELDS,
    ALLOWED_TAGS,
    ALLOWED_ORIGINS,
    ALLOWED_EMPLOYEE_RANGES,
    ALLOWED_COMPANY_TYPES,
    LINK_TYPES,
)
from awesome_media.utils.strings import url_to_filename


def _normalize_string_or_list(value):
    """Normalize a field that can be a single string or a list of strings."""
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()]
    if isinstance(value, list):
        return sorted(list({str(v).strip() for v in value if v}))
    return []


class Company:
    def __init__(self, filepath, data):
        self.filepath = filepath
        self.raw_data = data
        self._errors = []

        # 1. Normalize Fields
        self.name = str(data.get("name", ""))
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

        # 3. Normalize Labels
        self.origin = _normalize_string_or_list(data.get("origin"))
        self.employees = str(data.get("employees", "")).strip()
        self.company_type = _normalize_string_or_list(data.get("company_type"))

        # 4. Normalize Links
        raw_links = data.get("links", [])
        self.links = []
        if isinstance(raw_links, list):
            for item in raw_links:
                if isinstance(item, dict):
                    link_type = str(item.get("type", "")).strip().lower()
                    if not link_type:
                        link_type = "other"
                    self.links.append({
                        "url": str(item.get("url", "")).strip(),
                        "type": link_type,
                    })

        # 5. Normalize Tags
        raw_tags = data.get("tags", [])
        self.tags = sorted(list({
            str(t).strip().lower().replace(" ", "-").replace("/", "-").replace("--", "-")
            for t in raw_tags if t
        }))

    def to_dict(self):
        return {
            "name": self.name,
            "origin": self.origin,
            "employees": self.employees,
            "company_type": self.company_type,
            "description": self.description,
            "website_url": self.website_url,
            "website_text": self.website_text,
            "links": self.links,
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
                f"Please use tags from the allowed list."
            )

        # D. Validate Origin
        invalid_origins = [o for o in self.origin if o not in ALLOWED_ORIGINS]
        if invalid_origins:
            self._errors.append(
                f"Invalid origin values: {invalid_origins}. "
                f"Allowed: {ALLOWED_ORIGINS}"
            )

        # E. Validate Employees
        if self.employees and self.employees not in ALLOWED_EMPLOYEE_RANGES:
            self._errors.append(
                f"Invalid employees value: '{self.employees}'. "
                f"Allowed: {ALLOWED_EMPLOYEE_RANGES}"
            )

        # F. Validate Company Type
        invalid_types = [t for t in self.company_type if t not in ALLOWED_COMPANY_TYPES]
        if invalid_types:
            self._errors.append(
                f"Invalid company_type values: {invalid_types}. "
                f"Allowed: {ALLOWED_COMPANY_TYPES}"
            )

        # G. Validate Link Types
        invalid_link_types = [l["type"] for l in self.links if l["type"] not in LINK_TYPES]
        if invalid_link_types:
            self._errors.append(
                f"Invalid link types: {invalid_link_types}. "
                f"Allowed: {LINK_TYPES}"
            )

        return len(self._errors) == 0

    def get_errors(self):
        return self._errors
