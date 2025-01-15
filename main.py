from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
import logging
import asyncio

# Токен бота
BOT_TOKEN = "7585576606:AAFyr0yt17ige9VP9Ytoq66MNgdWWg3TNzs"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# Настройка бота
bot = Bot(token=BOT_TOKEN)  # Удаляем parse_mode из конструктора
dp = Dispatcher()

# Устанавливаем режим HTML по умолчанию
async def set_default_parse_mode():
    bot.session.parse_mode = "HTML"

# Чаты и темы
CHAT_MAPPING = {
    -1002289821025: {"chat_id": -1002392400754, "topic_id": 11},  # РГ выдача СМИ -> СМИ
    -1002449246842: {"chat_id": -1002392400754, "topic_id": 9},   # РГ выдача УК -> УК
    -1002373431113: {"chat_id": -1002392400754, "topic_id": 10},  # РГ выдача Соцмедиа -> СОЦМЕДИА
}

# Пересылка сообщений с сохранением форматирования и ссылок
@dp.message()
async def forward_message(message: Message):
    if message.chat.id in CHAT_MAPPING:
        target = CHAT_MAPPING[message.chat.id]
        try:
            # Проверяем, есть ли текст с форматированием
            if message.text:
                await bot.send_message(
                    chat_id=target["chat_id"],
                    text=message.text,  # Передаём оригинальный текст
                    entities=message.entities,  # Сохраняем ссылки и форматирование
                    message_thread_id=target["topic_id"],
                )
            # Лог успешной отправки
            logger.info(f"Сообщение из чата {message.chat.id} переслано в {target['chat_id']} (тема {target['topic_id']})")
        except TelegramBadRequest as e:
            logger.error(f"Ошибка при пересылке сообщения из чата {message.chat.id}: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при обработке сообщения из чата {message.chat.id}: {e}")

# Главная функция
async def main():
    logger.info("Бот запущен и готов к работе")
    await set_default_parse_mode()  # Устанавливаем HTML как стандартную разметку
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка в боте: {e}")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
