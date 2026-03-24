from pydantic import BaseModel


class Settings(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"


settings = Settings()
