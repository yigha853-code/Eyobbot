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


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
  user_name = message.from_user.first_name
  user_id = message.from_user.id
  file_id = message.photo[-1].file_id

  caption = (
      f'📥 <b>አዲስ የክፍያ ደረሰኝ መጣ!</b>\n\nስም: {user_name}\nየተጠቃሚ ID:'
      f' <code>{user_id}</code>'
  )

  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          '✅ አረጋግጥ እና ቁጥር ስጥ', callback_data=f'approve_{user_id}'
      )
  )

  bot.send_photo(
      ADMIN_CHAT_ID,
      file_id,
      caption=caption,
      parse_mode='HTML',
      reply_markup=markup,
  )

  bot.reply_to(
      message,
      'የክፍያ ደረሰኝዎ ፎቶ ደርሷል! 🙏\nእባክዎ ትንሽ ይጠብቁ፣ ሲረጋገጥ'
      ' የሎተሪ ቁጥርዎ በራሱ ይላክልዎታል።',
  )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('approve_')
)
def callback_approve(call):
  if call.from_user.id != ADMIN_CHAT_ID:
    bot.answer_callback_query(call.id, '⚠️ ይህን ማድረግ የሚችሉት አድሚኑ ብቻ ናቸው!')
    return

  try:
    target_user_id = int(call.data.split('_')[1])
    used_numbers = load_data()

    if len(used_numbers) >= 2500:
      bot.answer_callback_query(
          call.id, '⚠️ ሁሉም የሎተሪ ቁጥሮች ተይዘዋል!', show_alert=True
      )
      return

    while True:
      lottery_num = random.randint(1, 2500)
      if lottery_num not in used_numbers:
        used_numbers.append(lottery_num)
        save_data(used_numbers)
        break

    user_msg = (
        f'🎉 እንኳን ደስ አለዎት! ክፍያዎ ተረጋግጧል።\n\nየእርስዎ ልዩ የሎተሪ ቁጥር:'
        f' <b>{lottery_num}</b> ✅\n\n(እጣው የሚወጣው ጳጉሜ 5 ነው! መልካም ዕድል!)'
    )
    bot.send_message(target_user_id, user_msg, parse_mode='HTML')

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=(
            f'{call.message.caption}\n\n<b>🟢 ተረጋግጧል! የተሰጠ ቁጥር:'
            f' {lottery_num}</b>'
        ),
        parse_mode='HTML',
        reply_markup=None,
    )
    bot.answer_callback_query(call.id, f'ቁጥር {lottery_num} ተልኳል!')

  except Exception as e:
    bot.answer_callback_query(call.id, f'ስህተት ተፈጥሯል: {str(e)}', show_alert=True)


def run_bot():
  bot.infinity_polling(timeout=60, long_polling_timeout=60)


if name == 'main':
  t = threading.Thread(target=run_bot)
  t.start()
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
