import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем токен из переменной среды
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден! Убедитесь, что переменная среды TOKEN установлена.")

# Храним режимы и последние списки пользователей
user_data = {}

def pick_random(options):
    return random.choice(options)

def pick_weighted(options):
    weighted_list = []
    for option in options:
        parts = option.split(':')
        if len(parts) == 2 and parts[1].isdigit():
            weighted_list.extend([parts[0]] * int(parts[1]))
        else:
            weighted_list.append(option)
    return random.choice(weighted_list) if weighted_list else None

def pick_sequential(user_id):
    if user_id in user_data and user_data[user_id]['options']:
        return user_data[user_id]['options'].pop(0)
    return "Список пуст!"

def get_funny_comment():
    comments = [
        "О да, это отличный выбор!",
        "Ну, держись!",
        "Я всегда знал, что у тебя хороший вкус!",
        "Судьба решила за тебя!",
        "Я бы выбрал так же!"
    ]
    return random.choice(comments)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне список вариантов через пробел, и я выберу один из них!")
    user_data[update.message.chat_id] = {'mode': 'random', 'options': []}

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        mode = context.args[0].lower()
        if mode in ['random', 'weighted', 'sequential']:
            user_data[update.message.chat_id]['mode'] = mode
            await update.message.reply_text(f"Режим выбора установлен: {mode}")
        else:
            await update.message.reply_text("Доступные режимы: random, weighted, sequential")
    else:
        await update.message.reply_text("Укажи режим после команды. Например: /mode random")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text.strip()

    if text.lower().startswith("/mode"):
        return

    options = [opt.strip() for opt in text.split() if opt.strip()]
    user_data[user_id]['options'] = options
    mode = user_data[user_id]['mode']

    if mode == 'random':
        choice = pick_random(options)
    elif mode == 'weighted':
        choice = pick_weighted(options)
    else:  # sequential
        choice = pick_sequential(user_id)

    funny_comment = get_funny_comment()
    await update.message.reply_text(f"{choice} \n{funny_comment}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь список вариантов через пробел.\nИспользуй /mode random|weighted|sequential для выбора режима."
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mode", set_mode))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен!")
app.run_polling()
