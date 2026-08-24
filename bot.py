import json
import os
import random
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = '8761289862:AAEW1pXAqyZDaq1_pXq1BxXSIa1CO6UMhf0'
bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = 8999779414
DATA_FILE = 'lottery_records.json'

app = Flask(name)


@app.route('/')
def home():
return 'Eyob Lottery Bot is running live!'



def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
      return json.load(f)
  return []


def save_data(used_numbers):
  with open(DATA_FILE, 'w') as f:
    json.dump(used_numbers, f)


@bot.message_handler(commands=['start'])
def send_welcome(message):
  welcome_text = (
      'ሰላም! ወደ እዮብ የመኪና ሎተሪ ማስቆረጫ ቦት እንኳን በደህና መጡ። 🚗🎉\n\n'
      '🔥 እጣው የሚወጣው በጳጉሜ 5 ስለሆነ አሁኑኑ እድልዎን ይሞክሩ! 🔥\n\n'
      'ሎተሪውን ለመቁረጥ ከዚህ በታች ባለው የቴሌብር አካውንት ክፍያ በመፈጸም **የክፍያ'
      ' ደረሰኝ (Screenshot) ፎቶ** ይላኩ። 📸\n\n'
      '📱 የቴሌብር አካውንት መረጃ:\n'
      '• የቴሌብር ቁጥር:
251924061127
\n'
      '• ስም: እዮብ\n\n'
      '👇 ከታች ያለውን አዝራር በመጫን የደረሰኝ ፎቶዎን ይላኩ!'
  )
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.add(types.KeyboardButton('📸 የክፍያ ደረሰኝ ለመላክ እዚህ ይጫኑ'))
  bot.send_message(
      message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup
  )


@bot.message_handler(
    func=lambda message: message.text == '📸 የክፍያ ደረሰኝ ለመላክ እዚህ ይጫኑ'
)
def prompt_for_receipt(message):
  bot.send_message(
      message.chat.id,
      'እባክዎ የቴሌብር/የባንክ ክፍያ ፈጽመው የደረሰኙን ስክሪንሾት ፎቶ አሁን ይላኩኝ። 📥',
  )


