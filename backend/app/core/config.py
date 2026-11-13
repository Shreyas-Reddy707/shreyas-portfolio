
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Fail-fast application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Runtime & Environment
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = Field(default=False)
    PROJECT_NAME: str = "Shreyas Portfolio API"
    API_V1_PREFIX: str = "/api/v1"

    # Zero-Config Local Docker Standard (Overridden via .env in Production)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        min_length=20,
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        min_length=10,
    )

    # Strict CORS Origins (Never allow "*" in production)
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Cryptographic Webhook & Next.js ISR Secrets (Min 32 chars / 128-bit entropy)
    GITHUB_WEBHOOK_SECRET: str = Field(..., min_length=32)
    GITHUB_PAT: str = Field(..., min_length=20)
    GITHUB_USERNAME: str = Field(default="shreyas-reddy", min_length=2)
    NEXTJS_REVALIDATE_SECRET: str = Field(..., min_length=32)
    NEXTJS_REVALIDATE_URL: str = Field(default="http://localhost:3000/api/revalidate")

    # Cloudflare Turnstile Bot Defense (Use Cloudflare test keys in local dev only)
    TURNSTILE_SITE_KEY: str = Field(..., min_length=10)
    TURNSTILE_SECRET_KEY: str = Field(..., min_length=10)

    # AI Routing & Daily Token Circuit Breaker ($0 Student Tiers)
    AI_PROVIDER: str = Field(default="gemini", pattern="^(ollama|gemini|groq)$")
    GEMINI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    DAILY_AI_TOKEN_BUDGET: int = Field(default=50000, ge=1000, le=500000)
    IP_HASH_PEPPER: str = Field(..., min_length=32)

    # Resend Email Delivery ($0 Free Tier)
    RESEND_API_KEY: str = Field(default="")
    CONTACT_NOTIFY_EMAIL: str = Field(default="shreyas.chemakoora@gmail.com")
    RESEND_FROM_EMAIL: str = Field(default="Shreyas Portfolio <onboarding@resend.dev>")

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def forbid_wildcard_origin(cls, v: list[str]) -> list[str]:
        if "*" in v:
            raise ValueError("Wildcard '*' in ALLOWED_ORIGINS is strictly forbidden.")
        return v


settings = Settings()  # type: ignore[call-arg]

