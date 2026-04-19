"""Telegram bot for measuring and monitoring internet speed."""

import asyncio
import logging
import os

import speedtest
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Get token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Environment variable BOT_TOKEN is not set!")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def run_speedtest() -> str:
    """Measure internet speed and return formatted results."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        # Measure speed and convert from bits/s to Mbit/s
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        ping = st.results.ping

        return (
            f"🚀 Speedtest Results:\n"
            f"⬇️ Download: {download_speed:.2f} Mbit/s\n"
            f"⬆️ Upload: {upload_speed:.2f} Mbit/s\n"
            f"🏓 Ping: {ping:.2f} ms"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"❌ Error measuring speed: {str(e)}"


async def scheduled_speedtest(chat_id: int):
    """Periodically measure speed and send results to the chat."""
    while True:
        # Wait 10 minutes (600 seconds) before each new measurement
        await asyncio.sleep(600)

        # To avoid blocking the async event loop,
        # run synchronous speedtest in a separate thread
        result_message = await asyncio.to_thread(run_speedtest)
        await bot.send_message(
            chat_id, f"🕒 Scheduled (every 10 min):\n\n{result_message}"
        )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handle /start command: run speedtest and start monitoring."""
    # Respond to user immediately
    await message.answer("⏳ Please wait, measuring speed...")

    # Start background task for regular checks (for this chat)
    # create_task allows the task to run independently in the background
    asyncio.create_task(scheduled_speedtest(message.chat.id))

    # Run initial speed measurement
    result_message = await asyncio.to_thread(run_speedtest)

    # Send results to user
    await message.answer(result_message)


async def main():
    """Start the bot and begin polling for updates."""
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")

    # Start polling (waiting for updates from Telegram)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
