"""معالجات أوامر ورسائل تيليجرام."""

from datetime import timedelta
from telegram import Update
from telegram.ext import ContextTypes

from utils import format_event, format_memories, parse_datetime


HELP = """أهلاً بك. أستطيع مساعدتك بالعربية.

الأوامر المتاحة:
/addtask نص المهمة — حفظ مهمة
/note نص الملاحظة — حفظ ملاحظة
/tasks — عرض المهام غير المنجزة
/notes — عرض الملاحظات
/done رقم — وضع مهمة كمنجزة
/events — عرض مواعيد الأسبوع
/addevent العنوان | 2026-08-20 14:30 | 60 — إضافة موعد
/deleteevent معرّف_الموعد — حذف موعد
/delete رقم — حذف مهمة أو ملاحظة
/help — عرض هذه المساعدة

يمكنك أيضاً الكتابة بشكل طبيعي، وسأجيبك باستخدام الذكاء الاصطناعي."""


def authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    allowed = context.application.bot_data["settings"].allowed_user_ids
    return not allowed or update.effective_user.id in allowed


async def reject_if_unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not authorized(update, context):
        await update.effective_message.reply_text("عذراً، هذا البوت غير مفعّل لحسابك.")
        return True
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    await update.message.reply_text(HELP)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    await update.message.reply_text(HELP)


async def add_memory(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str):
    if await reject_if_unauthorized(update, context): return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("اكتب النص بعد الأمر. مثال: /addtask الاتصال بالعميل غداً")
        return
    db = context.application.bot_data["db"]
    item_id = db.add(update.effective_user.id, kind, text)
    label = "المهمة" if kind == "task" else "الملاحظة"
    await update.message.reply_text(f"تم حفظ {label} برقم {item_id}.")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_memory(update, context, "task")


async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_memory(update, context, "note")


async def list_memories(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str | None = None):
    if await reject_if_unauthorized(update, context): return
    rows = context.application.bot_data["db"].list_items(update.effective_user.id, kind, kind == "task")
    await update.message.reply_text(format_memories(rows))


async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_memories(update, context, "task")


async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_memories(update, context, "note")


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("الاستخدام: /done رقم_المهمة")
        return
    ok = context.application.bot_data["db"].complete_task(update.effective_user.id, int(context.args[0]))
    await update.message.reply_text("تم تحديث المهمة." if ok else "لم أجد مهمة بهذا الرقم.")


async def delete_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("الاستخدام: /delete الرقم")
        return
    ok = context.application.bot_data["db"].delete_item(update.effective_user.id, int(context.args[0]))
    await update.message.reply_text("تم الحذف." if ok else "لم أجد عنصراً بهذا الرقم.")


async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    try:
        service = context.application.bot_data["calendar"]
        items = service.upcoming()
        text = "\n".join(format_event(event, service.settings.timezone) for event in items)
        await update.message.reply_text(text or "لا توجد مواعيد خلال الأسبوع القادم.")
    except Exception as exc:
        await update.message.reply_text(f"تعذر الوصول إلى التقويم: {exc}")


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    payload = " ".join(context.args)
    parts = [part.strip() for part in payload.split("|")]
    if len(parts) not in (2, 3):
        await update.message.reply_text("الاستخدام: /addevent العنوان | 2026-08-20 14:30 | 60")
        return
    service = context.application.bot_data["calendar"]
    start = parse_datetime(parts[1], service.settings.timezone)
    if not start:
        await update.message.reply_text("صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD HH:MM")
        return
    try:
        duration = int(parts[2]) if len(parts) == 3 else 60
        event = service.create_event(parts[0], start, start + timedelta(minutes=duration))
        await update.message.reply_text(f"تمت إضافة الموعد. المعرّف: {event['id']}")
    except Exception as exc:
        await update.message.reply_text(f"تعذر إضافة الموعد: {exc}")


async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    if not context.args:
        await update.message.reply_text("الاستخدام: /deleteevent معرّف_الموعد")
        return
    try:
        context.application.bot_data["calendar"].delete_event(context.args[0])
        await update.message.reply_text("تم حذف الموعد.")
    except Exception as exc:
        await update.message.reply_text(f"تعذر حذف الموعد: {exc}")


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update, context): return
    db = context.application.bot_data["db"]
    service = context.application.bot_data["calendar"]
    memories = format_memories(db.list_items(update.effective_user.id, pending_only=True))
    try:
        events_text = "\n".join(format_event(e, service.settings.timezone) for e in service.upcoming(hours=72, limit=10))
    except Exception:
        events_text = "تعذر جلب المواعيد حالياً."
    try:
        answer = context.application.bot_data["ai"].reply(update.message.text, memories, events_text)
        await update.message.reply_text(answer)
    except Exception as exc:
        await update.message.reply_text(f"تعذر الحصول على رد الذكاء الاصطناعي: {exc}")
