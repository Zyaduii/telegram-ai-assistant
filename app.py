"""نقطة تشغيل وكيل تيليجرام."""

import logging
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, Defaults
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from ai import GeminiAssistant
from calendar_service import CalendarService
from config import Settings
from db import Database
from handlers import (
    add_event, add_note, add_task, delete_event, delete_memory, done, events,
    help_command, notes, start, tasks, text_message,
)
from scheduler import send_daily_summary, send_hourly_reminders

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application(settings: Settings) -> Application:
    application = Application.builder().token(settings.telegram_token).defaults(
        Defaults(tzinfo=ZoneInfo(settings.timezone))
    ).build()
    application.bot_data["settings"] = settings
    application.bot_data["db"] = Database(settings.database_path)
    application.bot_data["calendar"] = CalendarService(settings)
    application.bot_data["ai"] = GeminiAssistant(settings)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("note", add_note))
    application.add_handler(CommandHandler("tasks", tasks))
    application.add_handler(CommandHandler("notes", notes))
    application.add_handler(CommandHandler("done", done))
    application.add_handler(CommandHandler("delete", delete_memory))
    application.add_handler(CommandHandler("events", events))
    application.add_handler(CommandHandler("addevent", add_event))
    application.add_handler(CommandHandler("deleteevent", delete_event))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    if application.job_queue:
        application.job_queue.run_repeating(send_hourly_reminders, interval=3600, first=30, name="hourly-reminders")
        hour, minute = (int(part) for part in settings.daily_summary_time.split(":", 1))
        application.job_queue.run_daily(
            send_daily_summary,
            time=time(hour=hour, minute=minute, tzinfo=ZoneInfo(settings.timezone)),
            name="daily-summary",
        )
    return application


def main():
    settings = Settings.from_env()
    logger.info("بدء تشغيل وكيل تيليجرام")
    application = build_application(settings)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
