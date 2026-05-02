from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AI GenPerf FinOps Intelligence Framework"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_finops"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    SECRET_KEY: str = "enterprise-secret-key-change-in-production-min-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ai-finops.enterprise.com",
    ]

    OPENAI_COST_PER_1K_TOKENS_INPUT: float = 0.03
    OPENAI_COST_PER_1K_TOKENS_OUTPUT: float = 0.06
    CLAUDE_COST_PER_1K_TOKENS_INPUT: float = 0.015
    CLAUDE_COST_PER_1K_TOKENS_OUTPUT: float = 0.075

    DATA_SIMULATION_TEAMS: int = 12
    DATA_SIMULATION_ENGINEERS_PER_TEAM: int = 8
    DATA_SIMULATION_MONTHS: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
