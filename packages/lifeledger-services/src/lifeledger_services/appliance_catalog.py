"""
Appliance and Consumer Device Intelligence Catalog.
Provides industry standard lifespans, manufacturer warranty guidelines,
and routine maintenance schedule intervals.
"""
from typing import Any, Dict, List, Optional

APPLIANCE_CATEGORIES = {
    "refrigerator": {
        "expected_lifespan_years": 12,
        "default_warranty_months": 12,
        "sealed_system_warranty_months": 60,
        "routine_maintenance_interval_days": 180,
        "maintenance_recommendation": "Vacuum condenser coils and replace water filter cartridge",
    },
    "dishwasher": {
        "expected_lifespan_years": 9,
        "default_warranty_months": 12,
        "routine_maintenance_interval_days": 90,
        "maintenance_recommendation": "Clean filter screen and run vinegar descaling cycle",
    },
    "washing_machine": {
        "expected_lifespan_years": 11,
        "default_warranty_months": 12,
        "routine_maintenance_interval_days": 90,
        "maintenance_recommendation": "Inspect inlet hoses for bulges and run tub-clean cycle",
    },
    "clothes_dryer": {
        "expected_lifespan_years": 13,
        "default_warranty_months": 12,
        "routine_maintenance_interval_days": 180,
        "maintenance_recommendation": "Deep clean lint trap ductwork to prevent fire hazards",
    },
    "hvac_heat_pump": {
        "expected_lifespan_years": 15,
        "default_warranty_months": 60,
        "compressor_warranty_months": 120,
        "routine_maintenance_interval_days": 90,
        "maintenance_recommendation": "Replace MERV 11 air filters and clear condensate drain line",
    },
    "water_heater": {
        "expected_lifespan_years": 10,
        "default_warranty_months": 72,
        "routine_maintenance_interval_days": 365,
        "maintenance_recommendation": "Flush sediment from bottom tank and test pressure relief valve",
    },
    "laptop_computer": {
        "expected_lifespan_years": 5,
        "default_warranty_months": 12,
        "routine_maintenance_interval_days": 180,
        "maintenance_recommendation": "Inspect battery cycle count and backup local vault keys",
    },
    "oled_television": {
        "expected_lifespan_years": 7,
        "default_warranty_months": 12,
        "routine_maintenance_interval_days": 365,
        "maintenance_recommendation": "Run pixel refresher cycle and update firmware",
    },
}

MANUFACTURER_DIRECTORY = {
    "Apple": {
        "support_phone": "1-800-275-2273",
        "support_url": "https://support.apple.com",
        "standard_warranty_months": 12,
        "extended_warranty_name": "AppleCare+",
    },
    "Samsung": {
        "support_phone": "1-800-726-7864",
        "support_url": "https://www.samsung.com/us/support/",
        "standard_warranty_months": 12,
        "extended_warranty_name": "Samsung Care+",
    },
    "Sony": {
        "support_phone": "1-800-222-7669",
        "support_url": "https://us.esupport.sony.com",
        "standard_warranty_months": 12,
        "extended_warranty_name": "Sony Protect Plus",
    },
    "Bosch": {
        "support_phone": "1-800-944-2904",
        "support_url": "https://www.bosch-home.com/us/owner-support",
        "standard_warranty_months": 12,
        "extended_warranty_name": "Bosch Appliance Service Plan",
    },
    "Tesla": {
        "support_phone": "1-888-518-3752",
        "support_url": "https://www.tesla.com/support",
        "standard_warranty_months": 48,
        "extended_warranty_name": "Tesla Extended Service Agreement (ESA)",
    },
    "Carrier": {
        "support_phone": "1-800-227-7437",
        "support_url": "https://www.carrier.com/residential/en/us/warranty/",
        "standard_warranty_months": 120,
        "extended_warranty_name": "Carrier Ten-Year Limited Warranty",
    },
}


class ApplianceCatalog:
    """Provides lifecycle intelligence for home appliances and consumer electronics."""

    @classmethod
    def get_category_info(cls, category_name: str) -> Optional[Dict[str, Any]]:
        norm = category_name.strip().lower().replace(" ", "_").replace("-", "_")
        for k, v in APPLIANCE_CATEGORIES.items():
            if k in norm or norm in k:
                return v
        return None

    @classmethod
    def get_manufacturer_info(cls, brand_name: str) -> Optional[Dict[str, Any]]:
        if not brand_name:
            return None
        brand_clean = brand_name.strip().title()
        return MANUFACTURER_DIRECTORY.get(brand_clean)

    @classmethod
    def estimate_remaining_lifespan(
        cls, category: str, purchase_year: int, current_year: int = 2026
    ) -> Dict[str, Any]:
        """Calculates expected retirement horizon based on average category longevity."""
        cat_info = cls.get_category_info(category)
        expected_years = cat_info["expected_lifespan_years"] if cat_info else 8
        age = max(0, current_year - purchase_year)
        remaining = max(0, expected_years - age)
        percent_consumed = min(100, int((age / expected_years) * 100))

        return {
            "expected_lifespan_years": expected_years,
            "current_age_years": age,
            "remaining_years": remaining,
            "percent_consumed": percent_consumed,
            "replacement_recommended": remaining <= 1,
        }
