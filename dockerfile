# انتخاب تصویر پایه مناسب با جدیدترین نسخه پایتون
FROM python:3.11-slim

# تعریف دایرکتوری کاری
WORKDIR /app

# کپی فایل requirements.txt به داخل دایرکتوری کاری
COPY requirements.txt /app/

# نصب پکیج‌ها
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# کپی کردن سایر فایل‌ها به دایرکتوری کاری
COPY . /app/

# فعال کردن محیط مجازی
CMD ["/opt/venv/bin/python", "main.py"]
