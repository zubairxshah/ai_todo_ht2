import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    BETTER_AUTH_SECRET: str = os.environ.get("BETTER_AUTH_SECRET", "")
    AUTH_URL: str = os.environ.get("AUTH_URL", "http://localhost:3000")

    def __init__(self) -> None:
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")


settings = Settings()
