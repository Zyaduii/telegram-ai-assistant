"""إعدادات المشروع وقراءة متغيرات البيئة."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"المتغير البيئي المطلوب غير موجود: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    gemini_api_key: str
    gemini_model: str
    database_path: str
    timezone: str
    daily_summary_time: str
    calendar_id: str
    google_credentials_json: str
    google_token_json: str
    allowed_user_ids: tuple[int, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
        ids: tuple[int, ...] = tuple(
            int(item.strip()) for item in raw_ids.split(",") if item.strip()
        )
        return cls(
            telegram_token=_required("TELEGRAM_BOT_TOKEN"),
            gemini_api_key=_required("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            database_path=os.getenv("DATABASE_PATH", "data/assistant.sqlite3"),
            timezone=os.getenv("TIMEZONE", "Asia/Riyadh"),
            daily_summary_time=os.getenv("DAILY_SUMMARY_TIME", "08:00"),
            calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            google_credentials_json=os.getenv("GOOGLE_CREDENTIALS_JSON", ""),
            google_token_json=os.getenv("GOOGLE_TOKEN_JSON", ""),
            allowed_user_ids=ids,
        )
