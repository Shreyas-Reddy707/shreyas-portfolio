
from pydantic import Field, field_validator, model_validator
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
    GITHUB_USERNAME: str = Field(default="Shreyas-Reddy707", min_length=2)
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

    @field_validator("GITHUB_WEBHOOK_SECRET", "NEXTJS_REVALIDATE_SECRET", "IP_HASH_PEPPER")
    @classmethod
    def validate_cryptographic_secrets(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 32:
            raise ValueError("Secret must contain at least 32 characters after trimming whitespace.")
        if len(set(trimmed)) < 4:
            raise ValueError("Secret has insufficient character entropy (repeated characters detected).")
        known_placeholders = {
            "replace_with_a_secure_random_string",
            "changethis_to_a_secure_random_string",
            "your_webhook_secret_here",
            "00000000000000000000000000000000",
            "11111111111111111111111111111111",
            "abcdefghijklmnopqrstuvwxyz123456",
            "replace_with_64_hex_char_secret_from_secrets_token_hex_32",
        }
        if trimmed.lower() in known_placeholders:
            raise ValueError(f"Secret value '{trimmed}' is a known placeholder and cannot be used.")
        return trimmed

    @model_validator(mode="after")
    def validate_production_and_staging_invariants(self) -> "Settings":
        cf_test_keys = {
            "1x0000000000000000000000000000000aa",
            "2x0000000000000000000000000000000aa",
            "3x0000000000000000000000000000000aa",
        }
        if self.APP_ENV in ("production", "staging"):
            if self.TURNSTILE_SECRET_KEY.lower() in cf_test_keys:
                raise ValueError(
                    f"Cloudflare Turnstile test secret key is forbidden in {self.APP_ENV}."
                )
            if "localhost:5432" in self.DATABASE_URL or "postgres:postgres@" in self.DATABASE_URL:
                raise ValueError(
                    "DATABASE_URL cannot use local development default credentials in production/staging."
                )
            if "localhost:6379" in self.REDIS_URL:
                raise ValueError(
                    "REDIS_URL cannot use local development default (localhost:6379) in production/staging."
                )
            for origin in self.ALLOWED_ORIGINS:
                if "localhost" in origin or "127.0.0.1" in origin:
                    raise ValueError(
                        f"Localhost origin '{origin}' is forbidden in {self.APP_ENV} ALLOWED_ORIGINS."
                    )
        return self


settings = Settings()  # type: ignore[call-arg]

