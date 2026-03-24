from typing import Any, Literal

from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    user_input: str = Field(..., description="Natural-language conversion request from the user.")
    model: str | None = Field(default=None, description="Optional Ollama model override.")


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    reasoning: str


class ConversionResult(BaseModel):
    tool_name: str
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str
    formula: str


class ConvertResponse(BaseModel):
    status: Literal["success", "fallback"]
    user_input: str
    model: str
    agent_reasoning: str
    tool_call: ToolCall
    result: ConversionResult
    explanation: str


class HealthResponse(BaseModel):
    status: str
    ollama_base_url: str
