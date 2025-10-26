import telebot

# 🔹 Твой токен
BOT_TOKEN = "8422721937:AAHfWAkaULSbKrHrdsZ9n8gCjfrAfMOrhjc"

bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 Список админов (ID пользователей Telegram)
admins = set()

# 🔹 Данные пользователей (анкета)
user_data = {}

# 🔹 Проверка соответствия требованиям
def check_requirements(age, version, participate):
    try:
        age = int(age)
    except:
        return False
    if age < 14:
        return False
    if "1.21.8" not in version and "1.21.94.01" not in version:
        return False
    if participate.lower() not in ["да", "yes", "ага"]:
        return False
    return True


# 🔹 Команда /start
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


# 🔹 Начало анкеты
@bot.message_handler(func=lambda m: m.text.lower() == "анкета")
def start_form(msg):
    user_data[msg.from_user.id] = {}
    bot.send_message(msg.chat.id, "1️⃣ Введи своё имя:")


# 🔹 Обработка шагов анкеты
@bot.message_handler(func=lambda m: m.from_user.id in user_data)
def process_form(msg):
    user_id = msg.from_user.id
    data = user_data[user_id]

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


# 🔹 Команда /admin
@bot.message_handler(commands=["admin"])
def add_admin(msg):
    if msg.from_user.id not in admins:
        admins.add(msg.from_user.id)
        bot.send_message(msg.chat.id, "✅ Ты добавлен как администратор.")
    else:
        bot.send_message(msg.chat.id, "⚠ Ты уже админ.")


# 🔹 Команда /unadmin
@bot.message_handler(commands=["unadmin"])
def remove_admin(msg):
    if msg.from_user.id in admins:
        admins.remove(msg.from_user.id)
        bot.send_message(msg.chat.id, "❎ Ты больше не админ.")
    else:
        bot.send_message(msg.chat.id, "⚠ Ты не был админом.")


# 🔹 Запуск
print("✅ Бот запущен...")
bot.polling(non_stop=True)
