"""
International Date Normalizer & Extraction Engine.
Extracts and normalizes ambiguous dates across international formats,
resolves month boundaries, and validates leap-year correctness.
"""
from datetime import date, datetime
import re
from typing import List, Optional

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


class InternationalDateParser:
    """Parses arbitrary date strings from OCR streams into standardized ISO dates."""

    @classmethod
    def parse(cls, date_str: str) -> Optional[date]:
        if not date_str:
            return None
        text = date_str.strip().lower()

        # 1. ISO 8601: YYYY-MM-DD
        m = re.match(r"^(\d{4})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])$", text)
        if m:
            return cls._safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

        # 2. Textual Month: "Oct 18, 2026" or "18 October 2026" or "October 18 2026"
        m = re.match(r"^([a-z]+)\s+(\d{1,2}),?\s+(\d{4})$", text)
        if m and m.group(1) in MONTH_MAP:
            return cls._safe_date(int(m.group(3)), MONTH_MAP[m.group(1)], int(m.group(2)))

        m = re.match(r"^(\d{1,2})\s+([a-z]+),?\s+(\d{4})$", text)
        if m and m.group(2) in MONTH_MAP:
            return cls._safe_date(int(m.group(3)), MONTH_MAP[m.group(2)], int(m.group(1)))

        # 3. European: DD.MM.YYYY
        m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", text)
        if m:
            return cls._safe_date(int(m.group(3)), int(m.group(2)), int(m.group(1)))

        # 4. Standard Slash: MM/DD/YYYY or DD/MM/YYYY
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)
        if m:
            p1, p2, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            # If p1 > 12, it must be DD/MM/YYYY
            if p1 > 12 >= p2:
                return cls._safe_date(year, p2, p1)
            # Default to MM/DD/YYYY
            return cls._safe_date(year, p1, p2)

        return None

    @staticmethod
    def _safe_date(year: int, month: int, day: int) -> Optional[date]:
        try:
            if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return date(year, month, day)
        except ValueError:
            return None
        return None

    @classmethod
    def extract_all_dates(cls, document_text: str) -> List[date]:
        """Finds all candidate dates in document text."""
        candidates = []
        words = re.findall(r"\b[A-Za-z0-9/.-]{6,20}\b", document_text)
        for w in words:
            parsed = cls.parse(w)
            if parsed and parsed not in candidates:
                candidates.append(parsed)
        return candidates
