from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    mongo_uri: str | None = None
    jwt_secret: str = 'supersecret'
    jwt_expires_in: int = 3600

settings = Settings()
