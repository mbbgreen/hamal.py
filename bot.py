import logging
import random
import threading
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8102914320:AAGhC_xrDzZfVzRDyN8xErwtFdlVeuGkopI"  # Replace with your bot token

# Bot name and trigger words
BOT_NAME = "چوپان"
BOT_TRIGGERS = ["چوپان", "chopan", "shepherd"]

# Random automated messages (with ISTP personality - logical, reserved but occasionally witty)
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
    "گله ساکته، یا من دارم کر میشم؟"
]

# Responses when bot is mentioned (cool, logical, slightly sarcastic - ISTP style)
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
        "مثل اینکه به من نیاز داری."
    ],
    "greeting": [
        "سلام، همین؟",
        "علیک.",
        "آره، منم اینجام.",
        "سلام، چیز مهمی هست یا همینجوری گفتی؟",
        "سلام، کوتاه و مختصر، مثل همیشه."
    ],
    "question": [
        "پاسخ‌های ساده برای سوال‌های پیچیده ندارم.",
        "خودت چی فکر می‌کنی؟",
        "جالبه که می‌پرسی.",
        "نمی‌دونم، و شاید لازم هم نیست بدونم.",
        "به نظرت من همه چیز رو می‌دونم؟",
        "سوال خوبیه. جوابش رو وقتی پیدا کردم بهت میگم."
    ]
}

# Dictionary to store chat IDs where the bot is active
active_chats = {}

# Function to send random message to chat
async def send_random_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    message = random.choice(AUTO_MESSAGES)
    await context.bot.send_message(chat_id=chat_id, text=message)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Add chat to active chats
    active_chats[chat_id] = True
    
    await update.message.reply_text(
        f"چوپان اینجاست. کارت رو بگو."
    )

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("من چوپانم. وقتی اسمم رو صدا بزنی، میشنوم. همین.")

# Function to respond when mentioned
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message."""
    chat_id = update.effective_chat.id
    
    # Add chat to active chats if it's not already there
    if chat_id not in active_chats:
        active_chats[chat_id] = True
    
    # Check if the bot's name is mentioned
    if any(trigger.lower() in update.message.text.lower() for trigger in BOT_TRIGGERS):
        # Determine the type of message
        if any(greeting in update.message.text.lower() for greeting in ["سلام", "درود", "hi", "hello"]):
            response_list = MENTION_RESPONSES["greeting"]
        elif "?" in update.message.text or "؟" in update.message.text or any(q in update.message.text.lower() for q in ["چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
            response_list = MENTION_RESPONSES["question"]
        else:
            response_list = MENTION_RESPONSES["general"]
        
        # Select and send a random response
        response = random.choice(response_list)
        # Add a small delay to make it seem more natural
        await asyncio.sleep(random.randint(1, 3))
        await update.message.reply_text(response)

# Periodic message sender
async def periodic_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send messages to all active chats periodically."""
    for chat_id in list(active_chats.keys()):
        try:
            await send_random_message(context, chat_id)
        except Exception as e:
            logger.error(f"Error sending to chat {chat_id}: {e}")
            # If the bot has been removed from a chat, remove it from active chats
            active_chats.pop(chat_id, None)

# Function to schedule periodic messages through job queue
def schedule_periodic_messages(application):
    # Schedule the job every 30 minutes (1800 seconds)
    application.job_queue.run_repeating(periodic_messages, interval=1800)

# Main function to run the bot
async def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule periodic messages
    schedule_periodic_messages(application)

    # Run the bot until the user presses Ctrl-C
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import asyncio
    
    print("چوپان آماده است...")
    asyncio.run(main())
