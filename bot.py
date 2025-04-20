#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import random

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================= Bot configuration ===================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # جایگزین با توکن واقعی

BOT_NAME = "چوپان"
BOT_TRIGGERS = ["چوپان", "chopan", "shepherd"]

AUTO_MESSAGES = [
    "فقط میخواستم بگم که گوسفندا رو شمردم، همه سر جاشون هستن.",
    "گاهی سکوت، بهترین پاسخه.",
    "حقیقت همیشه ساده‌تر از چیزیه که بهش فکر می‌کنید.",
    "من اینجام، فقط حوصله حرف زدن ندارم.",
    "حرف زیاد، نشانه دانش کم است.",
    "واقعیت‌ها رو نمیشه با احساسات تغییر داد.",
    "کار، بیشتر از حرف نتیجه میده.",
    "گاهی لازمه فاصله بگیری تا بهتر ببینی.",
    "من فقط چوب دستمو دنبال می‌کنم، نه نظر بقیه رو.",
    "به نظرم یه سکوت خوب، از یه حرف الکی بهتره.",
    "مشکل رو حل کن، بعد درباره‌ش حرف بزن.",
    "همه چیز داره آروم پیش میره... شاید زیادی آروم.",
    "گله ساکته، یا من دارم کر میشم؟",
]

MENTION_RESPONSES = {
    "general": [
        "بله؟ کاری داشتی؟",
        "چی می‌خوای؟",
        "اینجام.",
        "چوپان میشنوه.",
        "منو صدا زدی، پس حتماً مهمه.",
        "سرم شلوغه، کوتاه بگو.",
        "چی شده؟",
        "شنیدم اسمم رو گفتی.",
        "هوم؟",
        "اینجا یه چوپان هست که گوش میده.",
        "میشنوم.",
        "خب؟",
        "مثل اینکه به من نیاز داری.",
    ],
    "greeting": [
        "سلام، همین؟",
        "علیک.",
        "آره، منم اینجام.",
        "سلام، چیز مهمی هست یا همینجوری گفتی؟",
        "سلام، کوتاه و مختصر، مثل همیشه.",
    ],
    "question": [
        "پاسخ‌های ساده برای سوال‌های پیچیده ندارم.",
        "خودت چی فکر می‌کنی؟",
        "جالبه که می‌پرسی.",
        "نمی‌دونم، و شاید لازم هم نیست بدونم.",
        "به نظرت من همه چیز رو می‌دونم؟",
        "سوال خوبیه. جوابش رو وقتی پیدا کردم بهت میگم.",
    ],
}

# نگهداری چت‌های فعال
active_chats: dict[int, bool] = {}

# =============== Logging setup ===================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =============== Bot Handlers ===================

async def send_random_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    message = random.choice(AUTO_MESSAGES)
    await context.bot.send_message(chat_id=chat_id, text=message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    active_chats[chat_id] = True
    await update.message.reply_text("چوپان اینجاست. کارت رو بگو.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("من چوپانم. وقتی اسمم رو صدا بزنی، میشنوم. همین.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text or ""

    if chat_id not in active_chats:
        active_chats[chat_id] = True

    if any(trigger.lower() in text.lower() for trigger in BOT_TRIGGERS):
        lower = text.lower()
        if any(greet in lower for greet in ["سلام", "درود", "hi", "hello"]):
            responses = MENTION_RESPONSES["greeting"]
        elif "?" in text or "؟" in text or any(q in lower for q in ["چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
            responses = MENTION_RESPONSES["question"]
        else:
            responses = MENTION_RESPONSES["general"]

        response = random.choice(responses)
        # Optional: نمایش وضعیت تایپینگ
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        await context.bot.send_message(chat_id=chat_id, text=response)

async def periodic_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in list(active_chats.keys()):
        try:
            await send_random_message(context, chat_id)
        except Exception as e:
            logger.error(f"Error sending to chat {chat_id}: {e}")
            active_chats.pop(chat_id, None)

def schedule_periodic_messages(application: Application) -> None:
    # هر ۳۰ دقیقه یک پیام ارسال کن (اولی بلافاصله)
    application.job_queue.run_repeating(
        callback=periodic_messages,
        interval=1800,
        first=0,
    )

# ================= Main ===================

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # ثبت handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # زمان‌بندی پیام‌های دوره‌ای
    schedule_periodic_messages(app)

    logger.info("چوپان آماده است...")
    # این متد خودش loop و awaitهای لازم رو انجام می‌ده
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
