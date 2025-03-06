from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
Welcome to Apple Music Download Bot! 🎵
Use /help to learn how to download music.
"""
    await update.message.reply_text(welcome_message)
