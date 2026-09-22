import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    PROJECT_NAME: str = "Travel Planning Multi-Agent System"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")

    # Storage
    DB_PATH: Path = BASE_DIR / "travel_planner.db"

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "").strip()

    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "").strip()
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "travel-planning-multi-agent")

    # Front-end static directory
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    @classmethod
    def get_active_provider(cls) -> str:
        """Returns the primary active LLM provider or 'simulation' if none configured."""
        if cls.OPENAI_API_KEY:
            return "openai"
        elif cls.GEMINI_API_KEY:
            return "gemini"
        elif cls.GROQ_API_KEY:
            return "groq"
        return "simulation"

settings = Settings()
