import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Настройки приложения"""
    # Telegram Bot Token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен")

    # Database settings
    DB_HOST: str = os.getenv("DB_HOST")
    if not DB_HOST:
        raise ValueError("DB_HOST не установлен")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    if not DB_PORT:
        raise ValueError("DB_PORT не установлен")
    DB_NAME: str = os.getenv("DB_NAME")
    if not DB_NAME:
        raise ValueError("DB_NAME не установлен")
    DB_USER: str = os.getenv("DB_USER")
    if not DB_USER:
        raise ValueError("DB_USER не установлен")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD не установлен")

    # Database URL for SQLAlchemy
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Admin user IDs (comma-separated)
    ADMIN_IDS: list[int] = field(default_factory=list)

    def __post_init__(self):
        # Parse admin IDs
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

    @property
    def database_url(self) -> str:
        """Get appropriate database URL based on settings"""
        return self.DATABASE_URL


settings = Settings()
