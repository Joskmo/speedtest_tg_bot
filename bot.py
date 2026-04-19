"""Telegram bot for measuring and monitoring internet speed."""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile

from graph import generate_chart
from measurements import measure_all
from storage import add_measurement, get_recent_hours

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Environment variable BOT_TOKEN is not set!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_PATH = os.getenv("DATA_PATH", "/data/speedtest_data.json")


def run_measurements() -> str:
    """Run both speed measurements and save results."""
    results = measure_all()

    speedtest_result = results[0]
    wget_result = results[1]

    if speedtest_result:
        add_measurement(
            "speedtest",
            speedtest_result["download"],
            speedtest_result.get("upload"),
            speedtest_result.get("ping"),
            DATA_PATH,
        )

    if wget_result:
        add_measurement("wget", wget_result["download"], path=DATA_PATH)

    lines = ["\U0001f680 Speedtest Results:"]

    if speedtest_result:
        lines.append(
            f"\u2b07\ufe0f Speedtest Download: "
            f"{speedtest_result['download']} Mbit/s"
        )
        lines.append(
            f"\u2b06\ufe0f Speedtest Upload: "
            f"{speedtest_result['upload']} Mbit/s"
        )
        lines.append(
            f"\U0001f3d3 Speedtest Ping: {speedtest_result['ping']} ms"
        )

    if wget_result:
        lines.append(
            f"\u2b07\ufe0f Wget Download: {wget_result['download']} Mbit/s"
        )

    if not speedtest_result and not wget_result:
        lines.append("\u2b07\ufe0f Download: no data")

    return "\n".join(lines)


async def scheduled_speedtest(chat_id: int):
    """Periodically measure speed and send results to the chat."""
    while True:
        await asyncio.sleep(600)

        result_message = await asyncio.to_thread(run_measurements)
        st_data = await asyncio.to_thread(
            get_recent_hours, 24, "speedtest", DATA_PATH
        )
        wget_data = await asyncio.to_thread(
            get_recent_hours, 24, "wget", DATA_PATH
        )

        chart_buf = await asyncio.to_thread(
            generate_chart, st_data, wget_data
        )

        await bot.send_message(
            chat_id,
            f"\U0001f552 Scheduled (every 10 min):\n\n{result_message}",
        )
        await bot.send_photo(
            chat_id,
            BufferedInputFile(chart_buf.read(), filename="chart.png"),
        )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handle /start command: run speedtest and start monitoring."""
    await message.answer("\u23f3 Please wait, measuring speed...")

    asyncio.create_task(scheduled_speedtest(message.chat.id))

    result_message = await asyncio.to_thread(run_measurements)
    st_data = await asyncio.to_thread(
        get_recent_hours, 24, "speedtest", DATA_PATH
    )
    wget_data = await asyncio.to_thread(
        get_recent_hours, 24, "wget", DATA_PATH
    )

    chart_buf = await asyncio.to_thread(
        generate_chart, st_data, wget_data
    )

    await message.answer(result_message)
    await message.answer_photo(
        BufferedInputFile(chart_buf.read(), filename="chart.png")
    )


async def main():
    """Start the bot and begin polling for updates."""
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
