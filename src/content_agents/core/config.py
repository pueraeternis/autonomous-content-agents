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
    twitter_api_key: SecretStr | None = Field(default=None, alias="API_KEY")
    twitter_api_secret: SecretStr | None = Field(default=None, alias="API_KEY_SECRET")
    twitter_access_token: SecretStr | None = Field(default=None, alias="ACCESS_TOKEN")
    twitter_access_secret: SecretStr | None = Field(default=None, alias="ACCESS_TOKEN_SECRET")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
