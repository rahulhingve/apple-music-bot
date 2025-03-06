from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🎵 *Apple Music Download Bot Help* 🎵

*Available Commands:*
• /start - Start the bot
• /help - Show this help message
• /alac - Download music from Apple Music

*How to use /alac command:*
1. Get the album/track URL from Apple Music
2. Use format: `/alac [URL] [track numbers]`

*Examples:*
• Download specific tracks:
`/alac https://music.apple.com/album/xyz 1,2,3`

• Download entire album:
`/alac https://music.apple.com/album/xyz all`

*Note:* 
- Track numbers should be comma-separated
- Use 'all' to download entire album
- Please wait for download completion notification
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')
