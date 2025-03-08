import re
from telegram import Update
from telegram.ext import ContextTypes
from database.db_utils import add_request, update_gofile_link
from utils.downloader import MusicDownloader
from utils.zip_utils import create_zip
from utils.uploader import upload_to_gofile
import os
import logging

logger = logging.getLogger(__name__)

def validate_track_numbers(track_str):
    """Validate track numbers format"""
    if track_str.lower() == 'all':
        return True
    
    # Check if it's a single number
    if track_str.isdigit():
        return True
        
    # Check comma-separated numbers
    if re.match(r'^\d+(?:,\d+)*$', track_str):
        return True
        
    return False

def validate_apple_music_url(url):
    """Validate Apple Music URL format"""
    return url.startswith(('https://music.apple.com/', 'http://music.apple.com/'))

async def alac_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db_session):
    try:
        # Basic command format check
        if not context.args or len(context.args) != 2:
            await update.message.reply_text(
                "❌ Invalid command format!\n\n"
                "Examples:\n"
                "• For specific tracks:\n"
                "`/alac https://music.apple.com/album/xyz 1,2,3`\n\n"
                "• For entire album:\n"
                "`/alac https://music.apple.com/album/xyz all`"
            )
            return
        
        url = context.args[0]
        tracks = context.args[1]
        
        # Validate URL
        if not validate_apple_music_url(url):
            await update.message.reply_text(
                "❌ Invalid URL! Please provide a valid Apple Music URL."
            )
            return
            
        # Validate track numbers
        if not validate_track_numbers(tracks):
            await update.message.reply_text(
                "❌ Invalid track format!\n\n"
                "Use either:\n"
                "• Single track: '1'\n"
                "• Multiple tracks: '1,2,3'\n"
                "• All tracks: 'all'"
            )
            return
        
        # Add request to database
        request_id = add_request(db_session, update.effective_user.id, url, tracks)
        
        await update.message.reply_text(
            "✅ Download request received!\n\n"
            "You will be notified when your download is ready.\n"
            "Join our group for download links and updates:\n"
            "https://t.me/apple_music_bot_rahul"
        )
        logger.info(f"New download request {request_id} from user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in alac command: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error processing your request. Please try again later."
        )
