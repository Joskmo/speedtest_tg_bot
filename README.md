*Read this in [Russian](README.ru.md)*

# VPS Speedtest Telegram Bot 🚀

A lightweight Telegram bot built with Python and `aiogram` to measure and monitor your server's network performance.

## Features
- **Dual measurement sources:** Uses both `speedtest-cli` and `wget` (Selectel) to measure download speed independently. Results are reported separately for each source.
- **On-demand testing:** Instantly measures Download speed, Upload speed (speedtest-cli only), and Ping via the `/start` command.
- **Continuous monitoring:** Automatically runs speed tests every 10 minutes and sends results with a 24-hour chart directly to the chat.
- **24-hour charts:** Hourly aggregated charts with separate curves for each measurement source. Sent as an image with every report.
- **Persistent storage:** All measurements are stored in a compact JSON file on a Docker volume, surviving container restarts.
- **Dockerized:** Easy and clean deployment using Docker and Docker Compose.

## Prerequisites
- Docker and Docker Compose installed on your VPS.
- A Telegram Bot Token (you can get one from [@BotFather](https://t.me/BotFather)).

## Deployment

1. Clone the repository to your server:
   ```bash
   git clone <your-repository-url>
   cd speedtest_tg_bot
   ```

2. Create an `.env` file from the example and add your bot token:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set your `BOT_TOKEN`.

3. Build and run the bot in the background:
   ```bash
   docker compose up -d --build
   ```

## Usage
Simply send `/start` to your bot in Telegram. It will reply immediately, run both speed measurements, and begin the 10-minute periodic reporting task for that chat. Each report includes text results and a 24-hour speed chart.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token (required) | — |
| `DATA_PATH` | Path to the JSON data file | `/data/speedtest_data.json` |

## Project Structure

```
├── bot.py              # Main bot logic
├── storage.py          # JSON data storage and hourly aggregation
├── measurements.py     # Speed measurement methods (speedtest-cli + wget)
├── graph.py            # Chart generation with matplotlib
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
└── pyrightconfig.json  # Pyright LSP configuration
```
