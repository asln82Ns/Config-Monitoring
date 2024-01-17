# Config-Monitoring
*Specifically for Dagger Wield Service*
Telegram bot that monitors for key words in the config.log file and sends telegram messages when conditions are met.

### Intro
This is not battle tested. I have gotten it to work and it successfully sends me messages but it has not been running for weeks. There are many improvements that can be made.
# Setup

## 1. Setup Telegram Bot:
- Create a Telegram bot and obtain the bot token.
- Identify or create a Telegram group or chat where messages will be sent, and get its chat ID.

Talks about getting token ID:
https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
Talks about getting Bot initially set up.(from timestamps 0:38-1:36)
https://www.youtube.com/watch?v=vZtm1wuA2yc&t=38s

## 2. Python & Script Setup

Step 1: Install Python (if not already installed)
Ubuntu 22.04 typically comes with Python pre-installed. Check if Python is installed:
```
python3 --version
```
If it's not installed, install Python:
```
sudo apt update
sudo apt install python3
```

Step 2: Install PIP (Python Package Installer)
Check if PIP is installed:
```
pip3 --version
```
If it's not installed, install PIP:
```
sudo apt install python3-pip
```
Step 3: Install the python-telegram-bot Library
Install the library using PIP (**NOTE: This Needs to be sudo installed. Had errors w/ service when I didn't use sudo**):
```
sudo pip3 install python-telegram-bot
```
Step 4: Create the Python Script
Open a text editor to write the script. You can use nano or your preferred text editor:
```
nano monitor_log.py
```
Paste the script:
```
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
```

Replace your_telegram_bot_token and your_chat_id in the script with your actual Telegram bot token and chat ID.
Replace LOG_FILE_PATH with the full to config.log ( /home/dagger/config.log for example).
Save and exit the editor (in nano, press CTRL + X, then press Y to confirm, and hit Enter).

Step 5: Make the Script Executable
Change the script's permissions to make it executable:
```
chmod +x monitor_log.py
```
Step 6: Test the Script
Run the script to ensure it works correctly:
```
./monitor_log.py
```

## 2. Setup Service
*This would allow it to run in the background of your machine 24/7*

1. Create a systemd service file:
```
sudo nano /etc/systemd/system/logmonitor.service
```
2. Add the following content, adjusting the paths as necessary:
```
[Unit]
Description=Log Monitor Service

[Service]
ExecStart=/full/path/to/monitor_log.py
Restart=always
User=username
Group=groupname

[Install]
WantedBy=multi-user.target
```
Replace /full/path/to/monitor_log.py with the actual full path to your script, and username and groupname with your username and group ( Username & groupname for me were both dagger). 
*For Exec Start I used: ExecStart=/usr/bin/python3 /home/dagger/monitor_log.py*

3. Reload the systemd daemon:
```
sudo systemctl daemon-reload
```
4. Start the service:
```
sudo systemctl start logmonitor.service
```
5. Enable the service to start on boot:
```
sudo systemctl enable logmonitor.service
```
This sets up your script as a service, ensuring it runs continuously and restarts automatically if it crashes or the server is rebooted.


## Notes
Use BOTH these to restart after making changes to monitor script.
sudo systemctl daemon-reload
sudo systemctl restart logmonitor.service

To test you can modify the monitor.py script here ```if '[ERROR]' in line:``` to something that occurs more frequently and see if messages show up.
