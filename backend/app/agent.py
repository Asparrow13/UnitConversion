import json
import re

import httpx

from .config import settings
from .models import ConversionResult, ToolCall
from .tools import TOOLS, TOOL_DESCRIPTIONS

SYSTEM_PROMPT = """You are a unit-conversion agent.
You must choose exactly one tool from the available tools.
Return valid JSON with this schema:
{
  "tool_name": "tool_name_here",
  "arguments": {"value": 12.5},
  "reasoning": "short explanation"
}
Rules:
- Use only the listed tool names.
- Extract a single numeric value from the user request.
- If the user request is ambiguous, choose the closest matching supported tool.
- Return JSON only. No markdown.
"""


class ConversionAgent:
    def __init__(self, model: str | None = None, ollama_base_url: str | None = None):
        self.model = model or settings.default_model
        self.ollama_base_url = ollama_base_url or settings.ollama_base_url

    def convert(self, user_input: str) -> tuple[str, ToolCall, ConversionResult]:
        tool_call, status = self._select_tool(user_input)
        tool_function = TOOLS[tool_call.tool_name]
        result = tool_function(**tool_call.arguments)
        return status, tool_call, result

    def _select_tool(self, user_input: str) -> tuple[ToolCall, str]:
        try:
            return self._select_tool_with_llm(user_input), "success"
        except Exception:
            return self._fallback_tool_selection(user_input), "fallback"

    def _select_tool_with_llm(self, user_input: str) -> ToolCall:
        tools_text = "\n".join(
            f"- {name}: {description}" for name, description in TOOL_DESCRIPTIONS.items()
        )
        prompt = f"""Available tools:
{tools_text}

User request: {user_input}
"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{self.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()

        content = response.json()["message"]["content"]
        parsed = json.loads(content)
        tool_name = parsed["tool_name"]
        arguments = parsed.get("arguments", {})
        reasoning = parsed.get("reasoning", "Selected by LLM.")

        if tool_name not in TOOLS:
            raise ValueError(f"Unsupported tool selected: {tool_name}")
        if "value" not in arguments:
            raise ValueError("LLM response did not include a value argument.")

        return ToolCall(tool_name=tool_name, arguments={"value": float(arguments["value"])}, reasoning=reasoning)

    def _fallback_tool_selection(self, user_input: str) -> ToolCall:
        text = user_input.lower()
        value = self._extract_number(text)

        if self._matches_units(
            text,
            value,
            ("pound", "pounds", "lb", "lbs"),
            ("kilogram", "kilograms", "kg"),
        ):
            return ToolCall(
                tool_name="pounds_to_kilograms",
                arguments={"value": value},
                reasoning="Fallback matched pounds to kilograms.",
            )
        if self._matches_units(
            text,
            value,
            ("kilogram", "kilograms", "kg"),
            ("pound", "pounds", "lb", "lbs"),
        ):
            return ToolCall(
                tool_name="kilograms_to_pounds",
                arguments={"value": value},
                reasoning="Fallback matched kilograms to pounds.",
            )
        if self._matches_units(text, value, ("gallon", "gallons", "gal"), ("liter", "liters", "l")):
            return ToolCall(
                tool_name="gallons_to_liters",
                arguments={"value": value},
                reasoning="Fallback matched gallons to liters.",
            )
        if self._matches_units(text, value, ("meter", "meters", "m"), ("foot", "feet", "ft")):
            return ToolCall(
                tool_name="meters_to_feet",
                arguments={"value": value},
                reasoning="Fallback matched meters to feet.",
            )
        if self._matches_units(text, value, ("fahrenheit", "f"), ("celsius", "c")):
            return ToolCall(
                tool_name="fahrenheit_to_celsius",
                arguments={"value": value},
                reasoning="Fallback matched Fahrenheit to Celsius.",
            )
        if self._matches_units(
            text,
            value,
            ("mile per hour", "miles per hour", "mph"),
            ("kilometer per hour", "kilometers per hour", "km/h", "kph"),
        ):
            return ToolCall(
                tool_name="miles_per_hour_to_kilometers_per_hour",
                arguments={"value": value},
                reasoning="Fallback matched miles per hour to kilometers per hour.",
            )

        raise ValueError("Could not match the user request to a supported conversion.")

    @staticmethod
    def _extract_number(text: str) -> float:
        match = re.search(r"-?\d+(\.\d+)?", text)
        if not match:
            raise ValueError("No numeric value found in request.")
        return float(match.group())

    @staticmethod
    def _matches_units(
        text: str,
        value: float,
        source_terms: tuple[str, ...],
        target_terms: tuple[str, ...],
    ) -> bool:
        has_source = any(term in text for term in source_terms)
        has_target = any(term in text for term in target_terms)
        if not (has_source and has_target):
            return False

        value_text = ConversionAgent._value_variants(value)
        source_near_value = any(f"{variant} {term}" in text for variant in value_text for term in source_terms)
        target_near_value = any(f"{variant} {term}" in text for variant in value_text for term in target_terms)

        if source_near_value and not target_near_value:
            return True
        if target_near_value and not source_near_value:
            return False

        source_index = min(text.find(term) for term in source_terms if term in text)
        target_index = min(text.find(term) for term in target_terms if term in text)
        return source_index < target_index

    @staticmethod
    def _value_variants(value: float) -> tuple[str, ...]:
        if float(value).is_integer():
            integer_value = str(int(value))
            return integer_value, f"{value:.1f}"
        return str(value), f"{value:.1f}".rstrip("0").rstrip(".")
