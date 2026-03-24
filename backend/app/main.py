from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import ConversionAgent
from .config import settings
from .models import ConvertRequest, ConvertResponse, HealthResponse

app = FastAPI(
    title="Unit Conversion Agent API",
    description="FastAPI backend exposing an Ollama-driven unit conversion agent.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", ollama_base_url=settings.ollama_base_url)


@app.post("/convert", response_model=ConvertResponse)
def convert_units(payload: ConvertRequest) -> ConvertResponse:
    try:
        agent = ConversionAgent(model=payload.model)
        status, tool_call, result = agent.convert(payload.user_input)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    explanation = (
        f"The agent chose `{tool_call.tool_name}` and converted "
        f"{result.input_value} {result.input_unit} to {result.output_value} {result.output_unit}."
    )

    return ConvertResponse(
        status=status,
        user_input=payload.user_input,
        model=payload.model or settings.default_model,
        agent_reasoning=tool_call.reasoning,
        tool_call=tool_call,
        result=result,
        explanation=explanation,
    )
