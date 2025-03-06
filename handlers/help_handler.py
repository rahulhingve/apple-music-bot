from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
How to use the bot:

/alac [Apple Music URL] [track numbers]

Examples:
• /alac https://music.apple.com/album/xyz all
• /alac https://music.apple.com/album/xyz 1,3,5

Track numbers can be:
• 'all' for entire album
• Individual tracks like '1,3,5'
"""
    await update.message.reply_text(help_text)
