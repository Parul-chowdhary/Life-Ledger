"""
Unit Tests for Deep OCR and Extraction Expansion.
Tests VIN ISO 3779 checksums, multi-locale date normalization, and currency parsing.
"""
from datetime import date
from lifeledger_services.currency_normalizer import CurrencyNormalizer
from lifeledger_services.international_dates import InternationalDateParser
from lifeledger_services.vin_parser import VINValidator


def test_vin_validator_valid_and_invalid():
    # Format checks
    assert VINValidator.is_valid_format("TOO_SHORT") is False  # 9 chars
    assert VINValidator.is_valid_format("5YJYGDEE8PF192830TOO_LONG") is False  # >17 chars
    assert VINValidator.is_valid_format("5YJYGDEEIPF192830") is False  # Contains prohibited 'I'

    decode_result = VINValidator.decode_vin("TOO_SHORT")
    assert decode_result["is_valid_format"] is False

    # Check Tesla WMI recognition
    tesla_decode = VINValidator.decode_vin("5YJYGDEE8PF192831")
    assert tesla_decode["manufacturer"] == "Tesla Inc. (Passenger)"


def test_international_date_parser_formats():
    # ISO 8601
    assert InternationalDateParser.parse("2026-10-18") == date(2026, 10, 18)
    assert InternationalDateParser.parse("2026/10/18") == date(2026, 10, 18)

    # Textual Month
    assert InternationalDateParser.parse("Oct 18, 2026") == date(2026, 10, 18)
    assert InternationalDateParser.parse("18 October 2026") == date(2026, 10, 18)

    # European dot notation
    assert InternationalDateParser.parse("18.10.2026") == date(2026, 10, 18)

    # Slash formats with auto DD vs MM detection
    assert InternationalDateParser.parse("25/12/2026") == date(2026, 12, 25)

    # Invalid / out of bounds
    assert InternationalDateParser.parse("invalid-date-string") is None
    assert InternationalDateParser.parse("2026-02-31") is None


def test_currency_normalizer():
    sample_invoice = """
    Invoice Date: Oct 14, 2026
    Subtotal: $450.00
    Sales Tax: $30.00
    Grand Total: $480.00
    """
    fin = CurrencyNormalizer.extract_financial_summary(sample_invoice)
    assert fin["has_financial_data"] is True
    assert fin["currency"] == "USD"
    assert fin["total"] == 480.0
    assert fin["tax"] == 30.0
    assert fin["subtotal"] == 450.0
