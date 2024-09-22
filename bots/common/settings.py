from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    # Production Bot
    production_bot_api_url: str
    production_bot_token: str

    # Admin Bot
    admin_bot_api_url: str
    admin_bot_token: str

    # Logging
    log_dir: str

    model_config = SettingsConfigDict(
        env_file=".env.bots",
        case_sensitive=True,
    )


settings = BotSettings()
