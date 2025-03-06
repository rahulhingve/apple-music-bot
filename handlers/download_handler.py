from telegram import Update
from telegram.ext import ContextTypes
from database.db_utils import add_request, update_gofile_link
from utils.downloader import MusicDownloader
from utils.zip_utils import create_zip
from utils.uploader import upload_to_gofile
import os
import logging

logger = logging.getLogger(__name__)

async def alac_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db_session):
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "Please provide both URL and track numbers!\n"
                "Example: /alac https://music.apple.com/album/xyz 1,2,3"
            )
            return
        
        url = context.args[0]
        tracks = context.args[1]
        
        # Add request to database
        request_id = add_request(db_session, update.effective_user.id, url, tracks)
        
        await update.message.reply_text(
            "✅ Download request received!\n"
            "You will be notified when your download is ready."
        )
        logger.info(f"New download request {request_id} from user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in alac command: {str(e)}", exc_info=True)
        await update.message.reply_text(f"Error processing request: {str(e)}")
