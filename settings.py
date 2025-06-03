from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str
    PORT: int
    BOT_TOKEN: str
    app_url: str
    class Config:
        env_file = ".env"

settings = Settings()