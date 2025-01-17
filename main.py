from pyrogram import Client, filters
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

# Настройки для Userbot
userbot_api_id = 27748866  # Ваш API ID из Telegram
userbot_api_hash = "8118b3e80aa7e8fcc8cce522a15d0e3b"  # Ваш API Hash из Telegram

# Настройки для Bot
bot_token = "7585576606:AAFyr0yt17ige9VP9Ytoq66MNgdWWg3TNzs"  # Токен вашего бота

# Создание клиентов для Userbot и Bot
userbot = Client(name="userbot_session", api_id=userbot_api_id, api_hash=userbot_api_hash)
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Сопоставление исходных чатов с целевыми чатами и темами
chat_mapping = {
    -1002289821025: {"target_chat_id": -1002392400754, "message_thread_id": 11},
    -1002449246842: {"target_chat_id": -1002392400754, "message_thread_id": 9},
    -1002373431113: {"target_chat_id": -1002392400754, "message_thread_id": 10},
}

# Очередь для передачи сообщений
message_queue = asyncio.Queue()

# Обработчик сообщений для Userbot
@userbot.on_message(filters.chat(list(chat_mapping.keys())) & filters.bot)
def handle_message(client, message):
    source_chat_id = message.chat.id
    if source_chat_id in chat_mapping:
        asyncio.run(message_queue.put({
            "source_chat_id": source_chat_id,
            "message_id": message.id,
            "target_chat_id": chat_mapping[source_chat_id]["target_chat_id"],
            "message_thread_id": chat_mapping[source_chat_id]["message_thread_id"]
        }))
        print(f"Сообщение добавлено в очередь для пересылки из {source_chat_id}")

# Функция для обработки очереди сообщений
async def process_queue():
    while True:
        message_data = await message_queue.get()
        if message_data:
            try:
                # Пересылка сообщения без указания message_thread_id
                message = await userbot.get_messages(
                    chat_id=message_data["source_chat_id"],
                    message_ids=message_data["message_id"]
                )

                await bot.request(
                    "sendMessage",  # Имя метода Telegram API
                    {
                        "chat_id": message_data["target_chat_id"],
                        "text": message.text or "",
                        "message_thread_id": message_data.get("message_thread_id"),
                        "parse_mode": "HTML" # Проверяем, есть ли thread_id
                    }
                )
                print(f"Сообщение переслано в {message_data['target_chat_id']}")
            except Exception as e:
                print(f"Ошибка при пересылке сообщения: {e}")
        message_queue.task_done()

# Запуск Userbot и Bot
if __name__ == "__main__":
    print("Запуск Userbot и Bot...")
    userbot.start()  # Запускаем userbot

    loop = asyncio.get_event_loop()
    loop.create_task(process_queue())  # Обработка очереди ботом

    print("Бот работает. Для выхода нажмите CTRL+C.")
    try:
        executor.start_polling(dp, skip_updates=True)  # Aiogram bot запускается через long polling
    except KeyboardInterrupt:
        print("Остановка...")
    finally:
        userbot.stop()
