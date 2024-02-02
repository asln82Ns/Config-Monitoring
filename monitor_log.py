#!/usr/bin/env python3
import time
import os
import asyncio
from telegram import Bot

# Telegram bot settings
TOKEN = 'your_telegram_bot_token'
CHAT_ID = 'your_chat_id'

# Log file and error threshold
LOG_FILE_PATH = '/home/dagger/config.log'
ERROR_THRESHOLD = 10  # Adjust as needed
FINALIZATION_KEYWORD = 'finalized!'  # Adjust based on your log's keyword
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size, adjust as needed
HEALTH_CHECK_INTERVAL = 15 * 60  # 15 minutes

async def send_telegram_message(message):
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        log_error(f"Failed to send Telegram message: {e}")

def log_error(message):
    with open("error_log.txt", "a") as error_log:
        error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_last_chunk(file, size, last_position):
    file.seek(0, os.SEEK_END)
    file_end = file.tell()
    start = max(file_end - size, last_position)
    size_to_read = file_end - start
    file.seek(start)
    return file.read(size_to_read), file_end

def monitor_log_file():
    last_checked_position = 0
    last_health_check_time = time.time()

    while True:
        try:
            if os.path.exists(LOG_FILE_PATH):
                with open(LOG_FILE_PATH, 'r') as file:
                    chunk, new_position = get_last_chunk(file, CHUNK_SIZE, last_checked_position)
                    error_count = chunk.count('[ERROR]')
                    finalization_count = chunk.count(FINALIZATION_KEYWORD)

                    # Health check
                    current_time = time.time()
                    if current_time - last_health_check_time >= HEALTH_CHECK_INTERVAL:
                        health_message = f"Health Check: {finalization_count} finalizations detected in the last chunk."
                        asyncio.run(send_telegram_message(health_message))
                        last_health_check_time = current_time

                    # Error Check
                    if error_count >= ERROR_THRESHOLD:
                        message = (f"Error threshold reached: {error_count} errors detected in the last chunk. " +
                                   f"Chunk processed from byte {last_checked_position} to byte {new_position}.")
                        asyncio.run(send_telegram_message(message))

                    last_checked_position = new_position
        except Exception as e:
            log_error(f"Error reading log file: {e}")

        time.sleep(60)

if __name__ == "__main__":
    monitor_log_file()
