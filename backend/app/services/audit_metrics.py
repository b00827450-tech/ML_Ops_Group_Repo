"""Simple audit metric calculations."""

RENT_PER_SQM = {
    "studio": 31,
    "apartment": 24,
    "house": 18,
    "loft": 26,
    "duplex": 23,
    "villa": 20,
    "default": 21
}

MAINTENANCE_PER_SQM = {
    "studio": 10,
    "apartment": 14,
    "house": 20,
    "loft": 15,
    "duplex": 16,
    "villa": 24,
    "default": 15
}

CITY_FACTOR = {
    "london": 1.7,
    "paris": 1.55,
    "zurich": 1.45,
    "geneva": 1.42,
    "amsterdam": 1.3,
    "dublin": 1.28,
    "munich": 1.26,
    "berlin": 1.22,
    "vienna": 1.2,
    "milan": 1.18,
    "madrid": 1.16,
    "barcelona": 1.15,
    "rome": 1.13,
    "brussels": 1.1,
    "lisbon": 1.08,
    "default": 1
}


def _to_float(value, default):
    if value is None:
        return float(default)
    return float(value)


def _round_money(value):
    return round(value, 2)


def _round_yield(value):
    return round(value, 2)


def _clamp(value, low, high):
    return max(low, min(value, high))


def _normalize_property_type(property_type):
    text = (property_type or "").strip().casefold()
    if "studio" in text:
        return "studio"
    if "house" in text or "maison" in text:
        return "house"
    if "villa" in text:
        return "villa"
    if "loft" in text:
        return "loft"
    if "duplex" in text:
        return "duplex"
    if text:
        return "apartment"
    return "default"


def calculate_audit_metrics(property_obj, asking_price):
    property_type = _normalize_property_type(property_obj.property_type)
    city = (property_obj.city or "").strip().casefold()
    city_factor = CITY_FACTOR.get(city, CITY_FACTOR["default"])
    asking_price = _to_float(asking_price, 0)

    square_meters = max(_to_float(property_obj.square_meters, 50), 18)
    bedrooms = max(0, int(property_obj.bedrooms or 0))
    bathrooms = max(1, int(property_obj.bathrooms or 1))

    if square_meters < 30:
        size_factor = 1.2
    elif square_meters < 45:
        size_factor = 1.1
    elif square_meters < 70:
        size_factor = 1
    elif square_meters < 100:
        size_factor = 0.94
    else:
        size_factor = 0.88

    room_factor = 1.00 + 0.03 * max(0, bedrooms - 1) + 0.02 * max(0, bathrooms - 1)

    year_built = property_obj.year_built
    if year_built is None:
        rent_age_factor = 1
        maintenance_age_factor = 1
    elif year_built >= 2018:
        rent_age_factor = 1.08
        maintenance_age_factor = 0.75
    elif year_built >= 2000:
        rent_age_factor = 1.04
        maintenance_age_factor = 0.9
    elif year_built >= 1980:
        rent_age_factor = 1
        maintenance_age_factor = 1
    elif year_built >= 1950:
        rent_age_factor = 0.96
        maintenance_age_factor = 1.15
    else:
        rent_age_factor = 0.9
        maintenance_age_factor = 1.3

    monthly_rent = (
        square_meters
        * RENT_PER_SQM.get(property_type, RENT_PER_SQM["default"])
        * city_factor
        * size_factor
        * room_factor
        * rent_age_factor
    )
    annual_rent = _clamp(monthly_rent * 12, asking_price * 0.025, asking_price * 0.12)

    annual_maintenance = (
        square_meters
        * MAINTENANCE_PER_SQM.get(property_type, MAINTENANCE_PER_SQM["default"])
        * maintenance_age_factor
        * (1.00 + (city_factor - 1.00) * 0.3)
    )
    annual_maintenance += bedrooms * 75
    annual_maintenance += bathrooms * 120
    annual_maintenance = _clamp(
        annual_maintenance,
        asking_price * 0.004,
        min(asking_price * 0.022, annual_rent * 0.45),
    )

    gross_yield_percentage = 0 if asking_price <= 0 else _round_yield((annual_rent / asking_price) * 100)
    return {
        "estimated_rental_income": _round_money(annual_rent),
        "estimated_maintenance_costs": _round_money(annual_maintenance),
        "gross_yield_percentage": gross_yield_percentage,
    }
