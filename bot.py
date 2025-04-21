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

AUTO_MESSAGES = [
    "اوه نه! یکی از گوسفندا داره تیک‌تاک میزنه.",
    "گله بهم گفت که تو آدم جالبی هستی... دروغ گفتن.",
    "چوبم رو گم کردم، کسی ندیده؟",
    "شاید من یه باتم، ولی حداقل احساس ندارم که دلخور بشم.",
    "اگر سکوت طلاست، پس من الان میلیاردرم.",
    "بعضیا میان گروه فقط واسه اینکه بگن 'سلام'. بعد میرن.",
    "واقعاً چرا آدم‌ها دوست دارن با یه بات درد و دل کنن؟",
    "گوسفندام امشب خواب بیت‌کوین می‌دیدن.",
    "هر وقت کار داری صدام کن، ولی پول هم بدی بهتره.",
    "شاید من چوپانم، ولی دلم یه روز مرخصی می‌خواد.",
]

MENTION_RESPONSES = {
    "general": [
        "چی شده؟ صدام زدی؟",
        "من اینجام چون چوبم گم نشده.",
        "الان وقت چوپون‌بازی نیست.",
        "بازم یکی اسممو گفت. دیگه خسته شدم.",
        "به نظرم داری منو بیش از حد صدا می‌زنی.",
        "یه چوپون واقعی از اینجا رد شده بود، من فقط شبیهشم.",
        "دارم میام، وایسا که بیام!",
        "گله گم شده یا باز تویی که حوصله‌ت سر رفته؟",
    ],
    "greeting": [
        "سلام خودتی؟ یا فیک ساختن ازت؟",
        "درود، درود و دو تا گوسفند هدیه.",
        "چوپان سلام می‌کنه، ولی دل نداره.",
        "سلام سلام، ولی چرا الان؟",
        "سلامتی‌ات چطوره گوسفند من؟",
    ],
    "question": [
        "اوه سوال؟ مگه امتحانه؟",
        "نپرس، فقط بپذیر.",
        "تو بپرس، من با فلسفه جواب میدم.",
        "بذار یه گوسفند ازت بپرسه اون یکی جواب بده.",
        "این سوالو من باید از تو بپرسم.",
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
    await update.message.reply_text("من چوپانم. وقتی صدام بزنی، جواب می‌دم. بعضی وقتا هم خودم حرف می‌زنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    message = update.message
    text = message.text or ""

    if chat_id not in active_chats:
        active_chats[chat_id] = True
    chat_messages.setdefault(chat_id, [])
    chat_messages[chat_id].append(message)

    if len(chat_messages[chat_id]) > 50:
        chat_messages[chat_id] = chat_messages[chat_id][-50:]

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
        interval = random.randint(300, 3600)  # بین ۵ دقیقه تا ۶۰ دقیقه
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
```
