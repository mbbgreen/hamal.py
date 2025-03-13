import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# پیکربندی لاگ برای نمایش اطلاعات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- مدل ترنسفورمر با Self-Attention --------------------

class SelfAttention(nn.Module):
    def __init__(self, embed_size, heads):
        super(SelfAttention, self).__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        assert self.head_dim * heads == embed_size, "Embed size باید بر تعداد heads بخش‌پذیر باشد."
        
        self.values = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.keys = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.queries = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.fc_out = nn.Linear(heads * self.head_dim, embed_size)
    
    def forward(self, values, keys, queries, mask=None):
        N = queries.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], queries.shape[1]
        
        # تغییر شکل برای تقسیم به heads
        values = values.reshape(N, value_len, self.heads, self.head_dim)
        keys = keys.reshape(N, key_len, self.heads, self.head_dim)
        queries = queries.reshape(N, query_len, self.heads, self.head_dim)
        
        # محاسبه انرژی بین کوئری‌ها و کلیدها
        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])
        
        if mask is not None:
            energy = energy.masked_fill(mask == 0, float("-1e20"))
        
        attention = torch.softmax(energy / (self.embed_size ** (1/2)), dim=3)
        out = torch.einsum("nhql,nlhd->nqhd", [attention, values])
        out = out.reshape(N, query_len, self.heads * self.head_dim)
        out = self.fc_out(out)
        return out

class SimpleTransformer(nn.Module):
    def __init__(self, vocab_size, embed_size, heads):
        super(SimpleTransformer, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.self_attention = SelfAttention(embed_size, heads)
        # خروجی مدل به اندازه تعداد توکن‌هاست (برای دمو)
        self.fc = nn.Linear(embed_size, vocab_size)
    
    def forward(self, x):
        # ورودی: (batch, seq_len)
        embed = self.embedding(x)  # تبدیل به بردارهای ویژگی (batch, seq_len, embed_size)
        attn_out = self.self_attention(embed, embed, embed)
        # برای سادگی، میانگین بردارهای خروجی را می‌گیریم
        attn_mean = attn_out.mean(dim=1)
        output = self.fc(attn_mean)  # خروجی: (batch, vocab_size)
        return output

# -------------------- بخش Tokenization و دیکشنری‌های نمونه --------------------

# دیکشنری کوچک برای تبدیل کلمات به اندیس (برای دمو)
vocab = {
    "سلام": 0,
    "چطوری": 1,
    "حالت": 2,
    "خوب": 3,
    "ممنون": 4,
    "درود": 5,
    "دوست": 6,
    "ربات": 7,
    "چی": 8,
    "خبر": 9
}

# دیکشنری پاسخ‌های از پیش تعریف‌شده (برای مثال‌هایی که به صورت rule-based پاسخ داده می‌شوند)
predefined_responses = {
    0: "سلام دوست من!",
    1: "من خوبم، تو چطوری؟",
    2: "امیدوارم حالتون خوب باشه.",
    3: "سلام و درود بر شما!",
    4: "خب، چه خبر؟"
}

# تابع ساده برای تبدیل متن به لیست اندیس‌ها
def tokenize(text):
    tokens = text.split()
    indices = []
    for token in tokens:
        # اگر کلمه در دیکشنری نباشد، از اندیس 0 استفاده می‌شود
        indices.append(vocab.get(token, 0))
    return indices

# -------------------- تابع تولید پاسخ با استفاده از مدل --------------------

# پارامترهای مدل
vocab_size = len(vocab)
embed_size = 16
heads = 2

# ایجاد مدل (توجه کنید که مدل آموزش ندیده و پارامترها تصادفی هستند)
model = SimpleTransformer(vocab_size, embed_size, heads)
model.eval()  # قرار دادن مدل در حالت ارزیابی

def generate_response(message):
    # اگر پیام شامل "سلام" باشد، پاسخ rule-based داده می‌شود
    if "سلام" in message:
        return "چته گشنه؟"
    
    # در غیر این صورت از مدل ترنسفورمر استفاده می‌کنیم
    indices = tokenize(message)
    if len(indices) == 0:
        return "متوجه نشدم، لطفاً دوباره بیان کنید."
    
    # تبدیل به تنسور با شکل (1, seq_len)
    input_tensor = torch.tensor([indices], dtype=torch.long)
    with torch.no_grad():
        output_logits = model(input_tensor)
    
    # انتخاب اندیس با بیشترین مقدار خروجی
    predicted_token = torch.argmax(output_logits, dim=1).item()
    # انتخاب پاسخ از میان پاسخ‌های از پیش تعریف‌شده
    response = predefined_responses.get(predicted_token, "متوجه صحبتتون نشدم.")
    return response

# -------------------- ادغام با ربات تلگرام --------------------

def start(update, context):
    update.message.reply_text("ربات آماده پاسخگویی است!")

def handle_message(update, context):
    user_message = update.message.text
    response = generate_response(user_message)
    update.message.reply_text(response)

def main():
    # جایگزین کردن 'YOUR_TELEGRAM_BOT_TOKEN' با توکن واقعی ربات تلگرام شما
    updater = Updater("7473433081:AAH1ISzqMI1l6t6n_H9_JYvVfpvXj-Lzvik", use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

