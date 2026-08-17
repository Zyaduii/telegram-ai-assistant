"""أدوات تنسيق وتحليل بسيطة للرسائل العربية."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


AR_DAYS = {
    "السبت": 5,
    "الأحد": 6,
    "الاحد": 6,
    "الإثنين": 0,
    "الاثنين": 0,
    "الثلاثاء": 1,
    "الأربعاء": 2,
    "الاربعاء": 2,
    "الخميس": 3,
    "الجمعة": 4,
}


def local_now(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone))


def parse_datetime(text: str, timezone: str) -> datetime | None:
    """يفهم ISO أو YYYY-MM-DD HH:MM، وهي الصيغة الموصى بها للمستخدم."""
    value = text.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=ZoneInfo(timezone))
        except ValueError:
            continue
    return None


def format_event(event: dict, timezone: str) -> str:
    start = event.get("start", {})
    raw = start.get("dateTime") or start.get("date")
    title = event.get("summary", "بدون عنوان")
    if not raw:
        return f"• {title}"
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(ZoneInfo(timezone))
    when = dt.strftime("%Y-%m-%d %H:%M")
    event_id = event.get("id", "")
    return f"• {when} — {title} (المعرّف: {event_id})"


def format_memories(rows) -> str:
    if not rows:
        return "لا توجد عناصر محفوظة."
    return "\n".join(
        f"• [{row['id']}] {'مهمة منجزة' if row['completed'] else row['kind']}: {row['content']}"
        for row in rows
    )
