from pyrogram import Client, filters
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

# Настройки для Userbot
userbot_api_id = 27748866  # Ваш API ID из Telegram
userbot_api_hash = "8118b3e80aa7e8fcc8cce522a15d0e3b"  # Ваш API Hash из Telegram

# Настройки для Bot
bot_token = "7585576606:AAFyr0yt17ige9VP9Ytoq66MNgdWWg3TNzs"  # Токен вашего бота

# Создание клиентов для Userbot и Bot
userbot = Client(name="userbot_session", api_id=userbot_api_id, api_hash=userbot_api_hash)
bot = Bot(token=bot_token)
router = Router()
dp = Dispatcher()

# Сопоставление исходных чатов с целевыми чатами и темами
chat_mapping = {
    -1002289821025: {"target_chat_id": -1002392400754, "message_thread_id": 11},
    -1002449246842: {"target_chat_id": -1002392400754, "message_thread_id": 9},
    -1002373431113: {"target_chat_id": -1002392400754, "message_thread_id": 10},
}

# Очередь для передачи сообщений
message_queue = asyncio.Queue()



# Обработчик сообщений для Userbot
@userbot.on_message()
async def handle_message(client, message):
    print(f"Получено сообщение: {message.text} из чата {message.chat.id}")
    source_chat_id = message.chat.id
    if source_chat_id in chat_mapping:
        await message_queue.put({
            "source_chat_id": source_chat_id,
            "message_id": message.id,
            "target_chat_id": chat_mapping[source_chat_id]["target_chat_id"],
            "message_thread_id": chat_mapping[source_chat_id]["message_thread_id"]
        })
        print(f"Сообщение добавлено в очередь для пересылки из {source_chat_id}")

# Функция для обработки очереди сообщений
async def process_queue():
    while True:
        message_data = await message_queue.get()
        if message_data:
            try:
                # Извлечение содержимого сообщения через Userbot
                message = await userbot.get_messages(
                    chat_id=message_data["source_chat_id"],
                    message_ids=message_data["message_id"]
                )

                # Логируем содержимое сообщения и данные для отправки
                print(f"Получено сообщение из {message_data['source_chat_id']}: {message.text or ''}")
                print(f"Отправка в тему: {message_data['target_chat_id']}, "
                      f"Тема ID: {message_data['message_thread_id']}")

                # Отправка сообщения в нужную тему
                await bot.request(
                    chat_id=message_data["target_chat_id"],
                    text=message.text or "",  # Текст сообщения
                    message_thread_id=message_data["message_thread_id"]  # Указание темы
                )
                print(f"Сообщение переслано в {message_data['target_chat_id']} (Тред: {message_data['message_thread_id']})")
            except Exception as e:
                print(f"Ошибка при пересылке сообщения: {e}")
        message_queue.task_done()

# Настройка маршрутов для Aiogram
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Бот запущен и готов пересылать сообщения.")

# Основная функция для запуска ботов
async def main():
    dp.include_router(router)  # Подключаем маршруты
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем Userbot
    print("Запуск Userbot...")
    await userbot.start()
    print("Userbot успешно запущен.")

    # Запускаем обработку очереди сообщений
    asyncio.create_task(process_queue())

    # Запускаем Aiogram
    print("Запуск Aiogram Bot...")
    await dp.start_polling(bot)

# Запуск приложения
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка...")
