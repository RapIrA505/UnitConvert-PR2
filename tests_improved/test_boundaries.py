"""Added after the initial Cosmic Ray run: 9 real surviving mutants."""

import math

import pytest

import core


@pytest.mark.parametrize("function,value,expected", [
    (core.celsius_to_fahrenheit, -273.15, -459.67),
    (core.fahrenheit_to_celsius, -459.67, -273.15),
    (core.km_to_miles, 0, 0),
    (core.miles_to_km, 0, 0),
    (core.kg_to_pounds, 0, 0),
    (core.pounds_to_kg, 0, 0),
])
def test_inclusive_boundaries(function, value, expected):
    """Kill strict-to-inclusive comparison and raised lower-bound mutants."""
    assert function(value) == pytest.approx(expected, rel=1e-10, abs=1e-10)


@pytest.mark.parametrize("function,boundary", [
    (core.celsius_to_fahrenheit, -273.15),
    (core.fahrenheit_to_celsius, -459.67),
])
def test_just_below_absolute_zero(function, boundary):
    """Kill mutants that lower the forbidden-temperature threshold by 1."""
    with pytest.raises(ValueError):
        function(math.nextafter(boundary, -math.inf))


def test_fractional_pounds_to_kg():
    """A nonintegral quotient kills the surviving / -> // mutant."""
    assert core.pounds_to_kg(1) == pytest.approx(0.45359237001003544, rel=1e-10)


def test_integer_too_large_for_float():
    """Kill replacement of the OverflowError handler."""
    with pytest.raises(ValueError, match="слишком велико"):
        core.km_to_miles(10**400)


@pytest.mark.parametrize("function", [core.celsius_to_fahrenheit, core.miles_to_km, core.kg_to_pounds])
def test_result_overflow(function):
    """Cover the previously missed error branch for finite input overflow."""
    with pytest.raises(ValueError, match="Результат слишком велик"):
        function(1.79e308)


@pytest.mark.parametrize("value", [True, False])
def test_boolean_is_not_a_number(value):
    """Additional contract check: bool is an int subclass but is forbidden."""
    with pytest.raises(TypeError):
        core.kg_to_pounds(value)
