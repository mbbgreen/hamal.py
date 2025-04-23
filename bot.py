import logging
import random
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= Bot configuration ===================
BOT_TOKEN = "8102914320:AAGhC_xrDzZfVzRDyN8xErwtFdlVeuGkopI"

BOT_NAME = "چوپان"
BOT_TRIGGERS = ["چوپان", "chopan", "shepherd"]

# پیام‌های خودکار با حال و هوای میم‌های امروزی و طنز سنگین‌تر
AUTO_MESSAGES = [
    "اوه نه! یکی از گوسفندا رسیده به آخرین قسمت Stranger Things😂",
    "فردا صبح اگه نپرسیدن چرا قهوه نیاوردی، غیبم زده بودم!",
    "گله بهم گفت که تو آدم خاصی هستی... اوکی ولش کن، راست گفتن!",
    "چوبم اپدیت نیاز داره، کسی ورژن جدید داره؟",
    "یه چوپان واقعی می‌دونه که موز چیه، ولی من فقط باتم!",
    "در حال پیدا کردن باگ میگم: با وُیس میتونم دیگه موزیک پلی کنم؟",
    "وقتی سکوت طلاست، پس گروه ما الان مستعمره میم‌هاس!",
    "گوسفندام امشب خواب NFT می‌دیدن 🤯",
    "هر وقت کار داشتی صدام کن، ولی DM هم بده بهتره.",
    "شاید من چوپانم، ولی دلم یه روز مرخصی با اینترنت پرسرعت می‌خواد.",
]

# واکنش به ریپلای‌ها با میم‌های متداول
REPLY_RESPONSES = [
    "😂😂😂",
    "🥺🥺🥺 آقا چرا اینقدر کار دارین؟",
    "🔥🔥🔥 حالا چیکاره اینجا؟",
    "🎉 یکی خدایی این ریپلای رو لایک کنه!",
    "💀 اومدم از شدت خنده بمیرم!",
]

# جداول پاسخ‌ها به منشن با دیالوگ‌های به‌روز و میم‌های فارسی-انگلیسی
MENTION_RESPONSES = {
    "general": [
        "چی شده؟ صدام زدی یا صرفا اومدی استاتوس بذاری؟",
        "اینجام چون چوبم گم نشده، ولی حال خوشه!",
        "بازم یکی اسممو گفت، الان 10K سنسور رفت!",
        "یه چوپان واقعی از اینجا رد شده بود، این فقط کپی‌پسته.",
        "داره میشه شبیه استریم Twitch، همه ناظر هستن!",
    ],
    "greeting": [
        "سلام گوسفند من! چطوری؟",
        "Hey bro! صبح بخیر.",
        "درود، ولی کدوم سرور؟",
        "سلام سلام، سبکت تازه‌اس؟",
        "سلامتی‌ات چطوره؟ چای و قهوه آماده‌س؟",
    ],
    "question": [
        "اوه سوال؟ مگه تو quiz هستیم؟",
        "نپرس، فقط vibe رو نگه دار.",
        "تو بپرس، من جوابم مثل memecoin بی‌ثباته.",
        "این سوال رو باید از گوسفند بعدی بپرسی.",
        "چرا؟ چون میشه. پایان داستان!",
    ],
}

# نگهداری چت‌های فعال و پیام‌های اخیر
active_chats: dict[int, bool] = {}
chat_messages: dict[int, list] = {}

# =============== Logging setup ===================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =============== Bot Handlers ===================
async def send_random_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, reply_to_message_id=None) -> None:
    message = random.choice(AUTO_MESSAGES)
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_to_message_id=reply_to_message_id
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    active_chats[chat_id] = True
    chat_messages.setdefault(chat_id, [])
    await update.message.reply_text("چوپان اومد. کارت چیه؟")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("من چوپانم! منشن، ریپلای یا فقط زنگ بزن؛ یه میم واست دارم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    message = update.message
    text = message.text or ""

    # ثبت فعالیت چت
    if chat_id not in active_chats:
        active_chats[chat_id] = True
    chat_messages.setdefault(chat_id, [])
    chat_messages[chat_id].append(message)
    if len(chat_messages[chat_id]) > 50:
        chat_messages[chat_id] = chat_messages[chat_id][-50:]

    # واکنش به ریپلای روی پیام‌های بات
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        reaction = random.choice(REPLY_RESPONSES)
        await message.reply_text(reaction)
        return

    # وقتی اسم بات رو میارن
    if any(trigger.lower() in text.lower() for trigger in BOT_TRIGGERS):
        lower = text.lower()
        if any(greet in lower for greet in ["سلام", "hi", "hello", "درود"]):
            responses = MENTION_RESPONSES["greeting"]
        elif "?" in text or "؟" in text or any(q in lower for q in ["چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
            responses = MENTION_RESPONSES["question"]
        else:
            responses = MENTION_RESPONSES["general"]

        response = random.choice(responses)
        await message.reply_text(response)

async def periodic_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in list(active_chats.keys()):
        try:
            reply_to = None
            if chat_messages.get(chat_id) and random.random() < 0.4:
                msg = random.choice(chat_messages[chat_id])
                reply_to = msg.message_id
            await send_random_message(context, chat_id, reply_to_message_id=reply_to)
        except Exception as e:
            logger.error(f"Error sending to chat {chat_id}: {e}")
            active_chats.pop(chat_id, None)

async def schedule_random_periodic_messages(app: Application) -> None:
    while True:
        interval = random.randint(300, 3600)
        await asyncio.sleep(interval)
        await periodic_messages(app)

# ================= Main ===================

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    asyncio.get_event_loop().create_task(schedule_random_periodic_messages(app))

    logger.info("چوپان آماده است...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
