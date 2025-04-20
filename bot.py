import telebot
import time
import random
import threading
import schedule
from telebot.types import Message

# Bot configuration
API_TOKEN = "8102914320:AAGhC_xrDzZfVzRDyN8xErwtFdlVeuGkopI"  # Replace with your bot token
bot = telebot.TeleBot(API_TOKEN)

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

# Function to send random message to chat
def send_random_message(chat_id):
    message = random.choice(AUTO_MESSAGES)
    bot.send_message(chat_id, message)

# Dictionary to store chat IDs where the bot is active
active_chats = {}

# Handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    chat_id = message.chat.id
    
    # Add chat to active chats if it's not already there
    if chat_id not in active_chats:
        active_chats[chat_id] = True
    
    # Check if the bot's name is mentioned
    if any(trigger.lower() in message.text.lower() for trigger in BOT_TRIGGERS):
        respond_to_mention(message)

# Function to respond when mentioned
def respond_to_mention(message: Message):
    # Determine the type of message
    if any(greeting in message.text.lower() for greeting in ["سلام", "درود", "hi", "hello"]):
        response_list = MENTION_RESPONSES["greeting"]
    elif "?" in message.text or "؟" in message.text or any(q in message.text.lower() for q in ["چرا", "چطور", "کی", "کجا", "چه", "آیا"]):
        response_list = MENTION_RESPONSES["question"]
    else:
        response_list = MENTION_RESPONSES["general"]
    
    # Select and send a random response
    response = random.choice(response_list)
    # Add a small delay to make it seem more natural
    time.sleep(random.randint(1, 3))
    bot.reply_to(message, response)

# Schedule periodic messages for active chats
def schedule_messages():
    while True:
        for chat_id in list(active_chats.keys()):
            try:
                send_random_message(chat_id)
            except Exception as e:
                print(f"Error sending to chat {chat_id}: {e}")
                # If the bot has been removed from a chat, it might get an error
                # Remove the chat from active chats if there's an error
                active_chats.pop(chat_id, None)
        
        # Wait for 30 minutes (1800 seconds)
        time.sleep(1800)

if __name__ == "__main__":
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_messages)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Start the bot
    print("چوپان آماده است...")
    bot.polling(none_stop=True)

