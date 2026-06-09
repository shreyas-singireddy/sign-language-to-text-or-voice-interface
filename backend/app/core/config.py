from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str | None = None
    jwt_secret: str = 'supersecret'
    jwt_expires_in: int = 3600

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
