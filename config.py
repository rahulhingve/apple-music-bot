import os

# Telegram Bot Token (replace with your actual token)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Path to the apple-music-alac-atmos-downloader tool
TOOL_PATH = "/root/apple-music-alac-atmos-downloader"

# Database settings
DATABASE_URL = "sqlite:///music_bot.db"

# Gofile API settings (if needed)
# GOFILE_API_KEY = "YOUR_GOFILE_API_KEY"

# Download directory settings
DOWNLOAD_DIR = os.path.join(TOOL_PATH, "AM-DL downloads")

# General settings
MAX_RETRY_ATTEMPTS = 1
QUEUE_CHECK_INTERVAL = 30  # seconds
