"""UnitConvert 1.0: six unit conversions and explicit input validation."""

import math

__version__ = "1.0"
MILES_PER_KM = 0.621371
POUNDS_PER_KG = 2.2046226218


def _number(value):
    """Accept finite int/float values, excluding bool and strings."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Введите число, а не строку или логическое значение.")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("Число слишком велико.") from exc
    if not math.isfinite(result):
        raise ValueError("Число должно быть конечным.")
    return result


def _non_negative(value):
    """Lengths and masses cannot be negative."""
    result = _number(value)
    if result < 0:
        raise ValueError("Длина и масса не могут быть отрицательными.")
    return result


def _finite_result(value):
    """Reject an infinite result caused by floating-point overflow."""
    if not math.isfinite(value):
        raise ValueError("Результат слишком велик.")
    return value


def celsius_to_fahrenheit(value):
    """Degrees Celsius -> Fahrenheit; Celsius >= -273.15."""
    value = _number(value)
    if value < -273.15:
        raise ValueError("Температура ниже абсолютного нуля.")
    return _finite_result(value * (9 / 5) + 32)


def fahrenheit_to_celsius(value):
    """Degrees Fahrenheit -> Celsius; Fahrenheit >= -459.67."""
    value = _number(value)
    if value < -459.67:
        raise ValueError("Температура ниже абсолютного нуля.")
    return _finite_result((value - 32) * (5 / 8))


def km_to_miles(value):
    """Kilometres -> miles; kilometres >= 0."""
    return _finite_result(_non_negative(value) * MILES_PER_KM)


def miles_to_km(value):
    """Miles -> kilometres; miles >= 0."""
    return _finite_result(_non_negative(value) / MILES_PER_KM)


def kg_to_pounds(value):
    """Kilograms -> pounds; kilograms >= 0."""
    return _finite_result(_non_negative(value) * POUNDS_PER_KG)


def pounds_to_kg(value):
    """Pounds -> kilograms; pounds >= 0."""
    return _finite_result(_non_negative(value) / POUNDS_PER_KG)
