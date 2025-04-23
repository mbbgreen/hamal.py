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

# یوزرنیم باتت رو دقیق اینجا قرار بده (با @)
BOT_USERNAME = "@chopan_bot"

BOT_NAME = "چوپان"
BOT_TRIGGERS = ["چوپان", "chopan", "shepherd"]

# ============ پیام‌های دوره‌ای خودکار =============
AUTO_MESSAGES = [
    "💀 دوباره اومدم سرک بکشم ببینم اوضاع چطوره…",
    "😂 دارم با خودم حرف می‌زنم، ولی خب بد نیست دوستان هم بشنون!",
    "💡 امروز یه ایده‌ی عالی واسه میم جدید دارم.",
    "🎉 جشن میم داریم! یکی GIF بفرسته.",
    "🔥 گوسفندات رو نگه دار، دارم می‌یام!",
    "🤖 فقط منم یا همه دارن سر کدوم قسمت Stranger Things بحث می‌کنن؟",
    "📈 بیت‌کوین بالا رفته، گوسفندا هیچی نمی‌فهمن.",
    "🎶 یه ترک جدید برای استریمرها داریم.",
    "⚠️ هشدار! این بات ممکنه وسط بحث خاموش بشه.",
    "💬 این‌بار من شروع می‌کنم: سلام… صدا دارم؟",
    "💤 فکر نمی‌کنم خوابم بیاد، اینقدر میم دیده‌م.",
    "🚀 آماده‌اید موشک میم پرتاب کنیم؟",
    "🌌 امشب ستاره‌ها رو می‌بینم، ولی تو گروه شما جذاب‌ترن!",
    "📢 اعلامیه: چوپان می‌خواد چای بخوره، کی شیرینش کنه؟",
    "💰 امروز تو خواب دارم پول چاپ می‌کنم!",
    "🕵️‍♂️ کارآگاه میم‌ها برگشته به گروپ.",
    "🎲 بخت‌آزمایی میم: حدس بزن فردا چی می‌گم؟",
    "🖼️ عکس پروفایلمو عوض کردم، می‌بینی؟",
    "🦄 منم گاهی احساس می‌کنم اسب تک‌شاخم!",
    "🔔 زنگ خطر: بدون میم نپرس!",
]

# ============ واکنش به ریپلای‌ها =============
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

# ============ پاسخ به کلمات کلیدی ============
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
    # … تا ۵۰ کلمه و ۱۵۰ جواب
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
    msg = random.choice(AUTO_MESSAGES)
    await context.bot.send_message(
        chat_id=chat_id,
        text=msg,
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

    # ثبت فعالیت
    if chat_id not in active_chats:
        active_chats[chat_id] = True
    chat_messages.setdefault(chat_id, []).append(message)
    if len(chat_messages[chat_id]) > 50:
        chat_messages[chat_id] = chat_messages[chat_id][-50:]

    # ۱) ریپلای روی پیام بات
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        await message.reply_text(random.choice(REPLY_RESPONSES))
        return

    # ۲) واکنش به کلمات کلیدی
    for kw, replies in KEYWORD_RESPONSES.items():
        if kw in text:
            await message.reply_text(random.choice(replies))
            return

    # ۳) تشخیص منشن با آیدی بات
    is_bot_mentioned = any(
        e.type == "mention" and message.text[e.offset:e.offset + e.length].lower() == @choponvip_bot.lower()
        for e in entities
    )

    # ۴) یا اسم بات تو متن اومده
    if is_bot_mentioned or any(trigger in text for trigger in BOT_TRIGGERS):
        # تشخیص سلام/سوال/عمومی
        if any(g in text for g in ["سلام", "hi", "hello", "درود"]):
            pool = MENTION_RESPONSES["greeting"]
        elif any(q in text for q in ["?", "؟", "چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
            pool = MENTION_RESPONSES["question"]
        else:
            pool = MENTION_RESPONSES["general"]
        await message.reply_text(random.choice(pool))

async def periodic_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in list(active_chats.keys()):
        try:
            reply_to = None
            if chat_messages.get(chat_id) and random.random() < 0.5:
                msg = random.choice(chat_messages[chat_id])
                reply_to = msg.message_id
            await send_random_message(context, chat_id, reply_to_message_id=reply_to)
        except Exception as e:
            logger.error(f"Error in periodic_messages for {chat_id}: {e}")
            active_chats.pop(chat_id, None)

async def schedule_random_periodic_messages(app: Application) -> None:
    while True:
        # هر ۵ تا ۶۰ دقیقه یه بار
        interval = random.randint(300, 3600)
        await asyncio.sleep(interval)
        await periodic_messages(app)

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع تسک دوره‌ای
    asyncio.get_event_loop().create_task(schedule_random_periodic_messages(app))

    logger.info("چوپان آماده است…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
