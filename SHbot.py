import telebot
# ⬇️ НОВЫЕ ИМПОРТЫ для Webhooks
from flask import Flask, request
import os
import sys

# 🔹 Твой токен и настройки. Теперь берем ТОКЕН из переменных окружения!
# BOT_TOKEN = "8422721937:AAHfWAkaULSbKrHrdsZ9n8gCjfrAfMOrhjc"
# 1. Токен должен быть в переменной окружения Render для безопасности.
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
if not BOT_TOKEN:
    print("❌ Ошибка: Переменная окружения TELEGRAM_TOKEN не найдена.")
    sys.exit(1) # Завершаем работу, если токен не найден

bot = telebot.TeleBot(BOT_TOKEN)
# 2. Создаем Flask-приложение
server = Flask(__name__)

# 🔹 Список админов (ID пользователей Telegram)
# Примечание: При каждом перезапуске сервера (что нормально на хостинге) этот список будет пустым.
# Для постоянного хранения данных админов требуется база данных.
admins = set()

# 🔹 Данные пользователей (анкета)
user_data = {}

# 🔹 Проверка соответствия требованиям
def check_requirements(age, version, participate):
    try:
        age = int(age)
    except ValueError: # Проверяем, что возраст - это число
        return False
    if age < 14:
        return False
    # Избегаем сравнения строк, лучше использовать .find()
    if "1.21.8" not in version and "1.21.94.01" not in version:
        return False
    if participate.lower() not in ["да", "yes", "ага"]:
        return False
    return True


# 🔹 Команды и логика анкеты — ВСЕ ОСТАЛОСЬ БЕЗ ИЗМЕНЕНИЙ!
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "👋 Привет! Чтобы попасть в хаус, нужно заполнить анкету.\n"
        "⚠ Требования:\n"
        "- Версия игры: 1.21.8 (Java) или 1.21.94.01 (Bedrock)\n"
        "- Возраст: не младше 14 лет\n"
        "- Готовность участвовать в съёмках\n\n"
        "Если подходишь — напиши 'анкета'"
    )

@bot.message_handler(func=lambda m: m.text.lower() == "анкета")
def start_form(msg):
    user_data[msg.from_user.id] = {}
    bot.send_message(msg.chat.id, "1️⃣ Введи своё имя:")

@bot.message_handler(func=lambda m: m.from_user.id in user_data)
def process_form(msg):
    user_id = msg.from_user.id
    data = user_data[user_id]
    
    # ... Ваш код обработки анкеты (без изменений) ...
    
    if "name" not in data:
        data["name"] = msg.text
        bot.send_message(msg.chat.id, "2️⃣ Укажи возраст:")
        return

    if "age" not in data:
        data["age"] = msg.text
        bot.send_message(msg.chat.id, "3️⃣ Укажи версию игры (1.21.8 или 1.21.94.01):")
        return

    if "version" not in data:
        data["version"] = msg.text
        bot.send_message(msg.chat.id, "4️⃣ Bedrock или Java?")
        return

    if "edition" not in data:
        data["edition"] = msg.text
        bot.send_message(msg.chat.id, "5️⃣ Будешь участвовать в съёмках? (да/нет):")
        return

    if "participate" not in data:
        data["participate"] = msg.text
        bot.send_message(msg.chat.id, "6️⃣ Был ли в других хаусах? (да/нет):")
        return

    if "other_house" not in data:
        data["other_house"] = msg.text
        bot.send_message(msg.chat.id, "7️⃣ Введи ник в игре:")
        return

    if "nickname" not in data:
        data["nickname"] = msg.text

        # Проверка требований
        if not check_requirements(
            data["age"], data["version"], data["participate"]
        ):
            bot.send_message(msg.chat.id, "❌ Ты не подходишь по требованиям. Извини!")
            del user_data[user_id]
            return

        # Формируем текст анкеты
        text = (
            f"📋 Новая анкета!\n\n"
            f"👤 Имя: {data['name']}\n"
            f"🎂 Возраст: {data['age']}\n"
            f"🎮 Версия: {data['version']}\n"
            f"🧱 Издание: {data['edition']}\n"
            f"🎥 Участие в съёмках: {data['participate']}\n"
            f"🏠 Был в других хаусах: {data['other_house']}\n"
            f"🆔 Ник: {data['nickname']}\n"
            f"💬 Telegram: @{msg.from_user.username or 'без ника'}"
        )

        # Отправляем анкету всем админам
        for admin_id in admins:
            try:
                bot.send_message(admin_id, text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Анкета отправлена! Ожидай ответ от администрации. кидай завявку https://t.me/+scSuo2E3kI8xN2Vi ")
        del user_data[user_id]
        
# ... Ваш код команд /admin и /unadmin (без изменений) ...

@bot.message_handler(commands=["admin"])
def add_admin(msg):
    if msg.from_user.id not in admins:
        admins.add(msg.from_user.id)
        bot.send_message(msg.chat.id, "✅ Ты добавлен как администратор.")
    else:
        bot.send_message(msg.chat.id, "⚠ Ты уже админ.")


@bot.message_handler(commands=["unadmin"])
def remove_admin(msg):
    if msg.from_user.id in admins:
        admins.remove(msg.from_user.id)
        bot.send_message(msg.chat.id, "❎ Ты больше не админ.")
    else:
        bot.send_message(msg.chat.id, "⚠ Ты не был админом.")


# -----------------------------------------------------------
# ⬇️ НОВАЯ СЕКЦИЯ: ОБРАБОТЧИК WEBHOOKS
# -----------------------------------------------------------

# Это основной маршрут, куда Telegram будет отправлять сообщения.
# Путь /<BOT_TOKEN> используется для повышения безопасности.
@server.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    # Проверяем, что запрос пришел от Telegram и имеет правильный формат
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # Обрабатываем полученное обновление
        bot.process_new_updates([update])
        return '', 200 # Возвращаем 200 OK - сообщение принято
    return 'Bad Request', 403

# -----------------------------------------------------------
# ⬇️ НОВАЯ СЕКЦИЯ: ЗАПУСК СЕРВЕРА
# -----------------------------------------------------------

if __name__ == "__main__":
    print("✅ Бот запускается в режиме Webhooks...")
    
    # 3. Получаем URL нашего сервиса на Render и порт
    # Render предоставляет внешний hostname (URL) и порт через переменные окружения
    app_url = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    port = int(os.environ.get('PORT', 5000))
    
    # 4. УСТАНОВКА WEBHOOK
    # Сообщаем Telegram, куда отправлять сообщения: https://<URL_RENDER>/<TOKEN>
    if app_url:
        webhook_url = f"https://{app_url}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        print(f"🔗 Webhook установлен на: {webhook_url}")
    else:
        print("❌ Ошибка: Переменная RENDER_EXTERNAL_HOSTNAME не найдена. Невозможно установить Webhook.")
        
    # 5. Запускаем Flask-сервер на порту, который дал Render
    # Это заменило bot.polling(non_stop=True)
    server.run(host="0.0.0.0", port=port)
