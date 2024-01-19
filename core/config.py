from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

import os

load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str = os.environ.get("DB_HOST")
    DB_PORT: str = os.environ.get("DB_PORT")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASS: str = os.environ.get("DB_PASS")

    db_url: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    db_echo: bool = True

    api_v1_prefix: str = "/api/v1"

    SERVER_PROTOCOL: str
    SERVER_HOST: str
    SERVER_PORT: str

    MICROSERVICE_NAME: str
    STATIC_PATH: Path

    URL_TO_WORD_LIST: str
    DICTIONARY_BASE_URL: str
    IMAGE_PROVIDER1_URL: str
    IMAGE_PROVIDER_HOSTNAME: str


settings = Settings()


if __name__ == "__main__":
    print(str(settings).replace(" ", "\n"))
