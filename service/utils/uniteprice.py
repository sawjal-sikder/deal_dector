def calculate_unit_price(unit_amount, price):
    try:
        if not unit_amount or not price:
            return None
        parts = str(unit_amount).strip().split()
        if len(parts) != 2:
            return None
        qty_str, unit = parts
        qty = float(qty_str.replace(',', '.'))
        price = float(price)
        unit = unit.lower().rstrip('.')

        if unit in ('g', 'gram', 'grams'):
            unit_price = (price / qty) * 1000
        elif unit in ('kg', 'kilogram', 'kilograms', 'kilo'):
            unit_price = (price / (qty * 1000)) * 1000
        elif unit in ('ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'):
            unit_price = (price / qty) * 1000
        elif unit in ('l', 'liter', 'liters', 'litre', 'litres'):
            unit_price = (price / (qty * 1000)) * 1000
        elif unit in ('cl', 'centiliter', 'centiliters', 'centilitre', 'centilitres'):
            unit_price = (price / (qty * 10)) * 1000
        else:
            return None

        return round(unit_price, 2)
    except Exception:
        return None