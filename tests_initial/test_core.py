"""Initial tests, preserved before mutation analysis."""

import pytest

import core


@pytest.mark.parametrize("function,value,expected", [
    (core.celsius_to_fahrenheit, 0, 32),
    (core.celsius_to_fahrenheit, 100, 212),
    (core.celsius_to_fahrenheit, -40, -40),
    (core.fahrenheit_to_celsius, 32, 0),
    (core.fahrenheit_to_celsius, 212, 100),
    (core.fahrenheit_to_celsius, -40, -40),
    (core.km_to_miles, 1, 0.621371),
    (core.km_to_miles, 10, 6.21371),
    (core.miles_to_km, 0.621371, 1),
    (core.miles_to_km, 6.21371, 10),
    (core.kg_to_pounds, 1, 2.2046226218),
    (core.kg_to_pounds, 10, 22.046226218),
    (core.pounds_to_kg, 2.2046226218, 1),
    (core.pounds_to_kg, 22.046226218, 10),
])
def test_known_values(function, value, expected):
    assert function(value) == pytest.approx(expected, rel=1e-10, abs=1e-10)


@pytest.mark.parametrize("function,value", [
    (core.celsius_to_fahrenheit, -300),
    (core.fahrenheit_to_celsius, -500),
    (core.km_to_miles, -1),
    (core.miles_to_km, -1),
    (core.kg_to_pounds, -1),
    (core.pounds_to_kg, -1),
    (core.celsius_to_fahrenheit, float("nan")),
    (core.km_to_miles, float("inf")),
])
def test_invalid_numeric_values(function, value):
    with pytest.raises(ValueError):
        function(value)


@pytest.mark.parametrize("value", ["10", None])
def test_invalid_types(value):
    with pytest.raises(TypeError):
        core.kg_to_pounds(value)
