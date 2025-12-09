from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM Settings ---
    openai_api_key: SecretStr = Field(default="local-dev-key", alias="VLLM_API_KEY")
    openai_api_base: str = Field(default="http://localhost:8000/v1", alias="OPENAI_API_BASE")
    model_name: str = Field(default="google/gemma-3-27b-it", alias="MODEL_NAME")

    # --- App Settings ---
    log_level: str = "INFO"
    environment: str = "development"

    # --- Twitter/X Credentials ---
    twitter_api_key: SecretStr | None = None
    twitter_api_secret: SecretStr | None = None
    twitter_access_token: SecretStr | None = None
    twitter_access_secret: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
