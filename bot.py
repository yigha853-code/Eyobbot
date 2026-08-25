import os
import json
import random
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = "PUT_YOUR_NEW_BOT_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = 8999779414
DATA_FILE = "lottery_records.json"

app = Flask(__name__)


@app.route("/")
def home():
    return "Eyob Lottery Bot is running live!"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_lottery_number():
    used_numbers = load_data()

    available = [n for n in range(1, 2501) if n not in used_numbers]

    if not available:
        return None

    number = random.choice(available)

    used_numbers.append(number)
    save_data(used_numbers)

    return number


@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "🎉 እንኳን ወደ እዮብ የመኪና ሎተሪ ማስቆረጫ ቦት በደህና መጡ!\n\n"
        "💰 የሎተሪ ዋጋ: 2500 ብር\n\n"
        "📱 ቴሌብር ቁጥር:\n"
        "251924061127\n\n"
        "👤 ስም: እዮብ\n\n"
        "ክፍያ ከፈጸሙ በኋላ የደረሰኙን ፎቶ ይላኩ።"
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📸 ደረሰኝ ላክ")

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard
    )


@bot.message_handler(func=lambda m: m.text == "📸 ደረሰኝ ላክ")
def ask_receipt(message):
    bot.send_message(
        message.chat.id,
        "እባክዎ የክፍያ ደረሰኝ ፎቶውን ይላኩ።"
    )


@bot.message_handler(content_types=["photo"])
def receive_receipt(message):

    keyboard = types.InlineKeyboardMarkup()

    approve = types.InlineKeyboardButton(
        "✅ Approve",
        callback_data=f"approve_{message.chat.id}"
    )

    reject = types.InlineKeyboardButton(
        "❌ Reject",
        callback_data=f"reject_{message.chat.id}"
    )

    keyboard.add(approve, reject)

    caption = (
        f"🧾 አዲስ የክፍያ ደረሰኝ\n\n"
        f"👤 {message.from_user.first_name}\n"
        f"🆔 {message.chat.id}"
    )

    bot.send_photo(
        ADMIN_CHAT_ID,
        message.photo[-1].file_id,
        caption=caption,
        reply_markup=keyboard
    )

    bot.send_message(
        message.chat.id,
        "✅ ደረሰኝዎ ተቀብሏል። ማረጋገጫ በመጠባበቅ ላይ ነው።"
    )


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data.startswith("approve_"):

        user_id = int(call.data.split("_")[1])

        lottery_number = get_lottery_number()

        if lottery_number is None:
            bot.send_message(
                user_id,
                "❌ ሁሉም የሎተሪ ቁጥሮች ተጠቅመዋል።"
            )
            return

        bot.send_message(
            user_id,
            f"🎉 ክፍያዎ ተረጋግጧል!\n\n"
            f"🎟 የሎተሪ ቁጥርዎ: {lottery_number}\n\n"
            f"🍀 መልካም ዕድል!"
        )

        bot.answer_callback_query(
            call.id,
            "Approved Successfully"
        )

    elif call.data.startswith("reject_"):

        user_id = int(call.data.split("_")[1])

        bot.send_message(
            user_id,
            "❌ የላኩት ደረሰኝ አልተፈቀደም።"
        )

        bot.answer_callback_query(
            call.id,
            "Rejected"
        )


def run_bot():
    bot.infinity_polling()


if __name__ == "__main__":

    threading.Thread(target=run_bot).start()

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
