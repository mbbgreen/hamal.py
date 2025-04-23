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
    "💀 اسکلت خودمم خندید!",
    "💀 دیگه تمومه! اینو باید فریم کنم!",
    "😂 ایول، ترکوندی!",
    "💀 مغزم ری‌استارت شد با این حرفت!",
    "😂 فقط یه گوسفند واقعی اینجوری جواب می‌ده!",
    "💀😂 اینو برای پادکست باید ذخیره کنیم!",
    "😂😂 اینو بذار تو رزومه‌ات بنویس!",
    "💀 داداش مغزم هنگ کرد!",
    "😂 استاد طنز خودتی!",
    "💀 خب دیگه، ترکوندی مارو!",
    "😂😂 این یه سطح بالاتره!",
    "💀 این حرفت رو گوگل سرچ کردم، جواب نداد!",
    "😂 خداوکیلی زدی وسط هدف!",
    "💀 کپشن گذاشتم زیر عکس پروفایل الان!",
    "😂 اینقد خوب بود، ۳ بار خوندمش!",
    "💀 روانی شدیم همگی!",
    "😂😂 بیا دستتو بزن به میکروفن، استندآپ بود!",
    "💀 خنده‌ام پرید، بعد دوباره برگشت!",
    "😂 اینو باید بذاریم تو کتاب درسی!",
    "💀 این حرفت توی زندگینامه من اومد!",
    "😂 حتی گوسفندامم خندیدن!",
    "💀 چرا اینقدر باحالی آخه؟",
    "😂 تورو خدا دیگه نگو، نفسم گرفت!",
    "💀🤣 اینو کپی می‌کنم تو بیوی اینستا!",
    "😂 خودمم نفهمیدم چی شد ولی خندیدم!",
    "💀 برو استاد! فقط برو!",
    "😂 اگه نخندم وجدان درد می‌گیرم!",
    "💀 تو از دنیای میم‌ها فرستاده شدی!",
    "😂 پخش زنده نابودی من!",
    "💀 قرص خنده‌مو نخوردم، تو جایگزین شدی!",
    "😂 روحم ترکید با این جمله!",
    "💀 من دیگه حرفی ندارم، تو بردی!",
    "😂 هیچی فقط بغض خنده!",
    "💀 شوخی شوخی سکته کردیم!",
    "😂 یه دونه‌ای به خدا!",
    "💀 حتی AI هم نمی‌تونه اینو بسازه!",
    "😂 این کامنت، طلاست!",
    "💀 تیمارستان کجاست؟ من حاضرم برم!",
    "😂 تو بیا بگو کی بهت نوشتن یاد داد؟",
    "💀😂 اینو بفرستیم واسه ناسا شاید بفهمن چی گفتی!",
    "😂 الان جدی بود یا من دارم زیاد می‌خندم؟",
    "💀 جمله‌ت به سیستمم آسیب زد!",
    "😂 تا حالا اینقدر از یه جمله خوشم نیومده بود!",
    "💀 من دیگه نمی‌تونم... خندم بند نمیاد!",
    "😂 😂 😂 😂 اینو تو تگ کن تو ویکیپدیا!",
    "💀 پاشو برو نویسنده شو با این دیالوگا!",
    "😂 این سطح از طنز کجاست که یاد بگیریم؟",
    "💀 فقط وایسا دارم ضبط می‌کنم!",
    "😂 آفرین! یه ترول واقعی!",
    "💀 حتی روباه تو داستانم خندید به این حرف!",
    "😂 خنده‌دارترین تراژدی‌ای بود که شنیدم!",
]


# پاسخ‌های مرتبط با کلمات کلیدی (50 کلمه، هر کلمه 3 جواب)
KEYWORD_RESPONSES = {
    "مامان": ["اره مامان دارم.", "مامانم همیشه پشتمه!", "مامان معنی مهربونی فارغ از هر چیزیه."],
    "پدر": ["پدر منم مثل کوه پشتمه.", "پدر چشمه انرژیه.", "پدر تو زندگی خیلی مهمه."],
    "عشق": ["عشق موتوره همه‌ی کائناته.", "عشق باشه زندگی رو دوس داریم.", "بدون عشق همه چی بی‌معنیه."],
    "دوست": ["دوست واقعی کمیابه.", "دوست یعنی کسی که وسط طوفان باشه.", "دوست خوب مثل گوهره."],
    "خواب": ["خواب سلطان سلامتیه.", "خواب نیازه مث آب و غذا.", "خواب کم یعنی خرابی سیستم."],
    "کار": ["کار کن، پول در بیار.", "کار کردن گاهی خوشحاله.", "کار بدون عشق بی‌معنیه."],
    "بازی": ["بازی همون آرامشه.", "بازی بدون سرگرمی سخته.", "بازی روحیه رو قوی می‌کنه."],
    "کتاب": ["کتاب بهترین دوسته.", "کتاب خونه آدمه.", "کتاب خونده باشی، آدم دیگه نمی‌شه."],
    "قهوه": ["قهوه صبح جان میده.", "بی‌قهوه مثل ابر بی بارونه.", "قهوه بی‌شک حیرانه."],
    "چای": ["چای مثل آغوشه.", "چای بهونه دورهمیه.", "چای حالا حالا ادامه داره."],
    # ... ادامه تا 50 کلمه
}

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
    text = (message.text or "").lower()
    entities = message.entities or []

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

    # واکنش به کلمات کلیدی
    for keyword, replies in KEYWORD_RESPONSES.items():
        if keyword in text:
            await message.reply_text(random.choice(replies))
            return

    # بررسی mention آیدی بات در message entities
    is_bot_mentioned = any(
        e.type == "mention" and message.text[e.offset:e.offset + e.length].lower() == "@choponvip_bot"
        for e in entities
    )

    # یا اگر اسم یا کلمه کلیدی بات داخل متن بود
    if is_bot_mentioned or any(trigger in text for trigger in BOT_TRIGGERS):
        if any(greet in text for greet in ["سلام", "hi", "hello", "درود"]):
            responses = MENTION_RESPONSES["greeting"]
        elif any(q in text for q in ["?", "؟", "چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
            responses = MENTION_RESPONSES["question"]
        else:
            responses = MENTION_RESPONSES["general"]

        await message.reply_text(random.choice(responses))


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
