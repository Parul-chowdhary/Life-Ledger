"""
Multi-Currency & Financial Breakdown Extraction Engine.
Extracts invoice totals, subtotals, VAT/sales tax, and normalizes multi-currency symbols.
"""
import re
from typing import Any, Dict, Optional

CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "CAD": "CAD",
    "AUD": "AUD",
    "USD": "USD",
}


class CurrencyNormalizer:
    """Extracts and parses amounts and financial breakdown from document OCR text."""

    @classmethod
    def parse_amount(cls, text: str) -> Optional[float]:
        if not text:
            return None
        # Clean currency symbols and commas
        clean = re.sub(r"[^\d.]", "", text.strip())
        try:
            return float(clean)
        except ValueError:
            return None

    @classmethod
    def extract_financial_summary(cls, text: str) -> Dict[str, Any]:
        """Identifies total, subtotal, and tax amounts from document text."""
        currency = "USD"
        for sym, code in CURRENCY_SYMBOLS.items():
            if sym in text:
                currency = code
                break

        # Patterns for totals
        total = None
        m_total = re.search(
            r"\b(?:Grand Total|Amount Due|Balance Due|Total Paid|Total)[:\s]*\$?\s*([\d,]+(?:\.\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if m_total:
            total = cls.parse_amount(m_total.group(1))

        # Patterns for tax
        tax = None
        m_tax = re.search(
            r"\b(?:Tax|Sales Tax|VAT|GST)[:\s]*\$?\s*([\d,]+(?:\.\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if m_tax:
            tax = cls.parse_amount(m_tax.group(1))

        # Patterns for subtotal
        subtotal = None
        m_sub = re.search(
            r"\b(?:Subtotal|Net Amount)[:\s]*\$?\s*([\d,]+(?:\.\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if m_sub:
            subtotal = cls.parse_amount(m_sub.group(1))

        return {
            "currency": currency,
            "total": total,
            "subtotal": subtotal,
            "tax": tax,
            "has_financial_data": total is not None,
        }
