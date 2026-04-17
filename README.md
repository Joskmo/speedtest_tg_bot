*Read this in [Russian](README.ru.md)*

# VPS Speedtest Telegram Bot 🚀

A lightweight Telegram bot built with Python and `aiogram` to measure and monitor your server's network performance.

## Features
- **On-demand testing:** Instantly measures Download speed, Upload speed, and Ping via the `/start` command.
- **Continuous monitoring:** Automatically runs a background speed test every 10 minutes and sends the results directly to the chat.
- **Dockerized:** Easy and clean deployment using Docker and Docker Compose.

## Prerequisites
- Docker and Docker Compose installed on your VPS.
- A Telegram Bot Token (you can get one from [@BotFather](https://t.me/BotFather)).

## Deployment

1. Clone the repository to your server:
   ```bash
   git clone <your-repository-url>
   cd test-vps-bot
   ```

2. Open the `docker-compose.yml` file and replace the placeholder with your actual Telegram bot token:
   ```yaml
   environment:
     - BOT_TOKEN=your_token_here
   ```
   *(Alternatively, you can create an `.env` file and pass the variables from there depending on your compose setup).*

3. Build and run the bot in the background:
   ```bash
   docker compose up -d
   ```

## Usage
Simply send `/start` to your bot in Telegram. It will reply immediately, start measuring the current speed, and begin the 10-minute periodic reporting task for that chat.