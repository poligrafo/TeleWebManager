from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    database_url: str
    secret_key: str
    log_dir: str

    model_config = SettingsConfigDict(
        env_file=".env.backend",
        case_sensitive=True,
    )


settings = BackendSettings()
