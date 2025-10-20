"""
Бот, который отвечает на сообщения в Telegram.
Сначала определяются несколько функций-обработчиков.
Затем эти функции передаются в приложение и регистрируются в соответствующих местах.
После этого бот запускается и работает до тех пор, пока вы не нажмете Ctrl-C в командной строке.
"""

import logging
from logging.handlers import RotatingFileHandler
import os

# Настройка логирования: файл + вывод в консоль
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "bot.log")

file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
# Удаляем возможные хендлеры, чтобы не дублировать вывод при повторном импорте
if root_logger.handlers:
    root_logger.handlers.clear()
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)

# Запрещаем propagate, чтобы сообщения не шли в root и не писались другими глобальными хендлерами
logger.propagate = False

# Отключаем детальные логи библиотеки httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from model import chat_with_llm

import dotenv
# Загружаем переменные окружения из файла .env
try:
    env = dotenv.dotenv_values(".env")
    TELEGRAM_BOT_TOKEN = env["TELEGRAM_BOT_TOKEN"]
except FileNotFoundError:
    raise FileNotFoundError("Файл .env не найден. Убедитесь, что он существует в корневой директории проекта.")
except KeyError as e:
    raise KeyError(f"Переменная окружения {str(e)} не найдена в файле .env. Проверьте его содержимое.")


# Определим команды и функции-обработчики сообщений
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start. При старте бота пользователь получает приветственное сообщение."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Основная функция для обработки текстовых сообщений от пользователя с целью ответа на них с помощью AI."""
    user_message = update.message.text
    user = update.effective_user.first_name     
    user_message = f'{user_message}. Имя пользователя: {user}'
    # Получаем историю сообщений из context.chat_data
    history = context.chat_data.get("history", [])
    logger.debug(f"History: {history}")

    # Передаем текущий запрос и историю сообщений в llm_service
    llm_response = chat_with_llm(user_message, history=history)
    context.chat_data["history"] = history  # сохраняем обновленную историю
    await update.message.reply_text(llm_response)


def main() -> None:
    """Функция инициализации бот-приложения."""
    # Создание основного объекта приложения Telegram API
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчик всех текстовых сообщений без команды
    chat_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, chat)  

    # Регистрируем обработчики:
    # Команда /start
    application.add_handler(CommandHandler("start", start))
    # Все остальные текстовые сообщения обрабатываются chat_handler
    application.add_handler(chat_handler)

    # Запуск бота в режиме постоянного ожидания команд.
    # Бот работает до прекращения программы (нажатие Ctrl-C или завершение по другому сигналу)
    application.run_polling(allowed_updates=Update.ALL_TYPES)  


if __name__ == "__main__":
    main()
