from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🎵 *Apple Music Download Bot Help* ��\n\n"
        "Join this group for download links:\n"
        "https://t\.me/apple\_music\_bot\_rahul\n\n"
        "*Available Commands:*\n"
        "• /start \- Start the bot\n"
        "• /help \- Show this help message\n"
        "• /alac \- Download music from Apple Music\n\n"
        "*How to use /alac command:*\n"
        "1\. Get the album/track URL from Apple Music\n"
        "2\. Use format: `/alac [URL] [track numbers]`\n\n"
        "*Examples:*\n"
        "• Download specific tracks:\n"
        "`/alac https://music\.apple\.com/album/xyz 1,2,3`\n\n"
        "• Download entire album:\n"
        "`/alac https://music\.apple\.com/album/xyz all`\n\n"
        "*Note:* \n"
        "\- Track numbers should be comma\-separated\n"
        "\- Use 'all' to download entire album\n"
        "\- Please wait for download completion notification"
    )
    await update.message.reply_text(
        text=help_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )
