"""
Vehicle Identification Number (VIN) Intelligence & ISO 3779 Checksum Validator.
Parses vehicle registration documents, decodes manufacturer World Manufacturer Identifiers (WMI),
and validates checksum digits.
"""
import re
from typing import Any, Dict, Optional

# Transliteration weights for ISO 3779 VIN checksum calculation
VIN_TRANSLITERATION = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
    "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9
}

VIN_POSITION_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

WMI_MANUFACTURERS = {
    "1HG": "Honda USA",
    "1FA": "Ford Motor Company",
    "1GC": "General Motors Chevrolet",
    "5YJ": "Tesla Inc. (Passenger)",
    "7SA": "Tesla Inc. (MPV/SUV)",
    "WAU": "Audi AG Germany",
    "WBA": "BMW AG Germany",
    "WDB": "Mercedes-Benz Germany",
    "JN1": "Nissan Japan",
    "JT2": "Toyota Japan",
}


class VINValidator:
    """Validates and parses 17-character ISO 3779 VINs extracted from vehicle service slips."""

    @staticmethod
    def is_valid_format(vin: str) -> bool:
        if not vin or len(vin) != 17:
            return False
        # VINs never contain letters I, O, Q to avoid confusion with numbers 1, 0
        return bool(re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin.upper()))

    @classmethod
    def calculate_check_digit(cls, vin: str) -> str:
        vin = vin.upper()
        total = 0
        for i, char in enumerate(vin):
            val = VIN_TRANSLITERATION.get(char, 0)
            total += val * VIN_POSITION_WEIGHTS[i]

        remainder = total % 11
        return "X" if remainder == 10 else str(remainder)

    @classmethod
    def verify_checksum(cls, vin: str) -> bool:
        if not cls.is_valid_format(vin):
            return False
        vin = vin.upper()
        expected = cls.calculate_check_digit(vin)
        actual = vin[8]  # Check digit is at position 9 (index 8)
        return expected == actual

    @classmethod
    def decode_vin(cls, vin: str) -> Dict[str, Any]:
        vin = vin.strip().upper()
        valid_format = cls.is_valid_format(vin)
        valid_check = cls.verify_checksum(vin) if valid_format else False

        wmi = vin[:3] if len(vin) >= 3 else ""
        manufacturer = WMI_MANUFACTURERS.get(wmi, "Unknown Manufacturer")

        return {
            "vin": vin,
            "is_valid_format": valid_format,
            "is_valid_checksum": valid_check,
            "wmi": wmi,
            "manufacturer": manufacturer,
            "model_year_code": vin[9] if len(vin) >= 10 else None,
            "serial_number": vin[11:] if len(vin) == 17 else None,
        }
