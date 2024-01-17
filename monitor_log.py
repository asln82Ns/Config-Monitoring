#!/usr/bin/env python3
import time
import os
import asyncio
from telegram import Bot

# Telegram bot settings
TOKEN = 'your_telegram_bot_token'
CHAT_ID = 'your_chat_id'

# Log file and error threshold
LOG_FILE_PATH = '/path/to/config.log'
ERROR_THRESHOLD = 5  # Adjust as needed

async def send_telegram_message(message):
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        log_error(f"Failed to send Telegram message: {e}")
        # Implement retry logic if needed

def log_error(message):
    with open("error_log.txt", "a") as error_log:
        error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def monitor_log_file():
    error_count = 0
    last_size = 0

    while True:
        try:
            if os.path.exists(LOG_FILE_PATH):
                current_size = os.path.getsize(LOG_FILE_PATH)

                if current_size < last_size:
                    last_size = 0

                if current_size > last_size:
                    with open(LOG_FILE_PATH, 'r') as file:
                        file.seek(last_size, 0)
                        for line in file:
                            if '[ERROR]' in line:
                                error_count += 1

                                if error_count >= ERROR_THRESHOLD:
                                    asyncio.run(send_telegram_message(f"Error threshold reached: {error_count} errors detected."))
                                    error_count = 0

                    last_size = current_size
        except Exception as e:
            log_error(f"Error reading log file: {e}")

        time.sleep(60)

if __name__ == "__main__":
    monitor_log_file()
