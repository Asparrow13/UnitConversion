from collections.abc import Callable

from .models import ConversionResult


ToolFunction = Callable[..., ConversionResult]


def kilograms_to_pounds(value: float) -> ConversionResult:
    converted = value * 2.20462
    return ConversionResult(
        tool_name="kilograms_to_pounds",
        input_value=value,
        input_unit="kg",
        output_value=round(converted, 4),
        output_unit="lb",
        formula="lb = kg * 2.20462",
    )


def pounds_to_kilograms(value: float) -> ConversionResult:
    converted = value / 2.20462
    return ConversionResult(
        tool_name="pounds_to_kilograms",
        input_value=value,
        input_unit="lb",
        output_value=round(converted, 4),
        output_unit="kg",
        formula="kg = lb / 2.20462",
    )


def gallons_to_liters(value: float) -> ConversionResult:
    converted = value * 3.78541
    return ConversionResult(
        tool_name="gallons_to_liters",
        input_value=value,
        input_unit="gal",
        output_value=round(converted, 4),
        output_unit="L",
        formula="L = gal * 3.78541",
    )


def meters_to_feet(value: float) -> ConversionResult:
    converted = value * 3.28084
    return ConversionResult(
        tool_name="meters_to_feet",
        input_value=value,
        input_unit="m",
        output_value=round(converted, 4),
        output_unit="ft",
        formula="ft = m * 3.28084",
    )


def fahrenheit_to_celsius(value: float) -> ConversionResult:
    converted = (value - 32) * 5 / 9
    return ConversionResult(
        tool_name="fahrenheit_to_celsius",
        input_value=value,
        input_unit="F",
        output_value=round(converted, 4),
        output_unit="C",
        formula="C = (F - 32) * 5 / 9",
    )


def miles_per_hour_to_kilometers_per_hour(value: float) -> ConversionResult:
    converted = value * 1.60934
    return ConversionResult(
        tool_name="miles_per_hour_to_kilometers_per_hour",
        input_value=value,
        input_unit="mph",
        output_value=round(converted, 4),
        output_unit="km/h",
        formula="km/h = mph * 1.60934",
    )


TOOLS: dict[str, ToolFunction] = {
    "kilograms_to_pounds": kilograms_to_pounds,
    "pounds_to_kilograms": pounds_to_kilograms,
    "gallons_to_liters": gallons_to_liters,
    "meters_to_feet": meters_to_feet,
    "fahrenheit_to_celsius": fahrenheit_to_celsius,
    "miles_per_hour_to_kilometers_per_hour": miles_per_hour_to_kilometers_per_hour,
}


TOOL_DESCRIPTIONS = {
    "kilograms_to_pounds": "Convert kilograms (kg) to pounds (lb). Argument: value.",
    "pounds_to_kilograms": "Convert pounds (lb) to kilograms (kg). Argument: value.",
    "gallons_to_liters": "Convert US gallons (gal) to liters (L). Argument: value.",
    "meters_to_feet": "Convert meters (m) to feet (ft). Argument: value.",
    "fahrenheit_to_celsius": "Convert Fahrenheit (F) to Celsius (C). Argument: value.",
    "miles_per_hour_to_kilometers_per_hour": "Convert miles per hour (mph) to kilometers per hour (km/h). Argument: value.",
}
