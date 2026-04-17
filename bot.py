import asyncio
import logging
import speedtest
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart


# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана!")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для измерения скорости интернета
def run_speedtest() -> str:
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        
        # Измеряем скорость и переводим из бит/с в Мбит/с
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        ping = st.results.ping
        
        return (
            f"🚀 Результаты Speedtest:\n"
            f"⬇️ Скачивание: {download_speed:.2f} Мбит/с\n"
            f"⬆️ Загрузка: {upload_speed:.2f} Мбит/с\n"
            f"🏓 Пинг: {ping:.2f} мс"
        )
    except Exception as e:
        return f"❌ Ошибка при измерении скорости: {str(e)}"

# Фоновая задача: запускается один раз при старте бота
async def scheduled_speedtest(chat_id: int):
    while True:
        # Ждем 10 минут (600 секунд) перед каждым новым измерением
        await asyncio.sleep(600)
        
        # Чтобы не блокировать асинхронный цикл (event loop), 
        # запускаем синхронный speedtest в отдельном потоке
        result_message = await asyncio.to_thread(run_speedtest)
        await bot.send_message(chat_id, f"🕒 Плановое (каждые 10 мин):\n\n{result_message}")

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # Мгновенно отвечаем пользователю
    await message.answer("⏳ Ожидайте, измерение скорости...")
    
    # Запускаем фоновую задачу для регулярных проверок (для этого чата)
    # create_task позволяет задаче работать независимо в фоне
    asyncio.create_task(scheduled_speedtest(message.chat.id))
    
    # Запускаем первичное измерение скорости
    result_message = await asyncio.to_thread(run_speedtest)
    
    # Отправляем результаты пользователю
    await message.answer(result_message)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен!")
    
    # Запуск поллинга (ожидания обновлений от Telegram)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")