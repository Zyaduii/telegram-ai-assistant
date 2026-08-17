"""وظائف دورية للتذكيرات والملخص الصباحي."""

from datetime import timedelta
from telegram.ext import ContextTypes
from utils import format_event, format_memories, local_now


async def send_hourly_reminders(context: ContextTypes.DEFAULT_TYPE):
    settings = context.application.bot_data["settings"]
    calendar = context.application.bot_data["calendar"]
    now = local_now(settings.timezone)
    events = calendar.events_starting_between(now + timedelta(minutes=55), now + timedelta(minutes=65))
    if not events:
        return
    for user_id in settings.allowed_user_ids:
        for event in events:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"تذكير: لديك موعد بعد ساعة تقريباً.\n{format_event(event, settings.timezone)}",
            )


async def send_daily_summary(context: ContextTypes.DEFAULT_TYPE):
    settings = context.application.bot_data["settings"]
    db = context.application.bot_data["db"]
    calendar = context.application.bot_data["calendar"]
    now = local_now(settings.timezone)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    events = calendar.events_starting_between(now.replace(hour=0, minute=0, second=0, microsecond=0), end)
    events_text = "\n".join(format_event(e, settings.timezone) for e in events) or "لا توجد مواعيد اليوم."
    for user_id in settings.allowed_user_ids:
        tasks = db.list_items(user_id, kind="task", pending_only=True)
        tasks_text = format_memories(tasks) if tasks else "لا توجد مهام معلقة."
        await context.bot.send_message(
            chat_id=user_id,
            text=f"صباح الخير. هذا ملخصك اليومي:\n\nالمهام:\n{tasks_text}\n\nالمواعيد:\n{events_text}",
        )
