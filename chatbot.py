import telebot
from telebot import types
import requests
from datetime import datetime

# ================= Konfiguratsiya =================
OPENROUTER_API_KEY = "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"
TG_TOKEN = "8083599108:AAF9MJjn-lppxhzSSJ46X30bNSBNS1XSZiM"
ADMIN_ID = 7789281265  # Sening Telegram ID’ing
USER_DAILY_LIMIT = 3  # Boshqalarga kunlik limit
CHANNEL_LINKS = [
    ("1-kanal", "https://t.me/web_saites"),
    ("2-kanal", "https://t.me/AI_SI_II")
]
# ==================================================

bot = telebot.TeleBot(TG_TOKEN)

# Foydalanuvchi limitlari
user_limits = {}  # {user_id: {"last_day": "YYYY-MM-DD", "count": int}}

# ================= GPT javobi ==================
def ask_gptoss(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    r = requests.post(url, json=data, headers=headers)
    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None  # Limit yoki xatolik

# ================= Uzun xabar ==================
def send_long_message(chat_id, text):
    for i in range(0, len(text), 4000):
        bot.send_message(chat_id, text[i:i+4000])

# ================= Limit tekshirish ==================
def check_limit(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in user_limits:
        user_limits[user_id] = {"last_day": today, "count": 0}
    if user_limits[user_id]["last_day"] != today:
        user_limits[user_id] = {"last_day": today, "count": 0}

    if user_id == ADMIN_ID:
        return True  # Sen cheksiz
    else:
        if user_limits[user_id]["count"] >= USER_DAILY_LIMIT:
            return False
        else:
            user_limits[user_id]["count"] += 1
            return True

# ================= Inline keyboard ==================
def channel_keyboard():
    markup = types.InlineKeyboardMarkup()
    for name, url in CHANNEL_LINKS:
        markup.add(types.InlineKeyboardButton(name, url=url))
    return markup

# ================= /start ==================
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    bot.send_message(
        user_id,
        "Botdan foydalanish uchun kanallarga obuna bo‘ling:",
        reply_markup=channel_keyboard()
    )

# ================= Har qanday xabar ==================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    # Limitni tekshirish
    if not check_limit(user_id):
        if user_id == ADMIN_ID:
            bot.send_message(user_id, "OpenRouter limit tugadi!")
        else:
            bot.send_message(user_id, "Bugun kunlik limit tugadi. Keyinroq urinib ko‘ring.")
        return

    # GPT javobi
    bot.send_message(user_id, "O'ylayapman...")
    answer = ask_gptoss(text)
    if answer:
        send_long_message(user_id, answer)
    else:
        if user_id == ADMIN_ID:
            bot.send_message(user_id, "OpenRouter limit tugadi!")
        else:
            bot.send_message(user_id, "Server xatoligi yuz berdi. Keyinroq urinib ko‘ring.")

# ================= Botni ishga tushurish ==================
bot.polling()