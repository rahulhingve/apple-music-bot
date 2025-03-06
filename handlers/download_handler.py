from telegram import Update
from telegram.ext import ContextTypes
from database.db_utils import add_request, update_gofile_link
from utils.downloader import MusicDownloader
from utils.zip_utils import create_zip
from utils.uploader import upload_to_gofile
import os

async def alac_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db_session):
    if len(context.args) < 2:
        await update.message.reply_text("Please provide both URL and track numbers!")
        return
        
    url = context.args[0]
    tracks = context.args[1]
    
    # Add request to database
    request_id = add_request(db_session, update.effective_user.id, url, tracks)
    
    await update.message.reply_text("Download request received! Processing...")
    
    try:
        # Download
        downloader = MusicDownloader("/root/apple-music-alac-atmos-downloader")
        download_dir = downloader.download(url, tracks)
        
        # Zip
        zip_path = create_zip(download_dir)
        
        # Upload
        gofile_url = upload_to_gofile(zip_path)
        
        if gofile_url:
            # Update database
            update_gofile_link(db_session, request_id, gofile_url)
            
            # Send link to user
            await update.message.reply_text(f"Download ready: https://{gofile_url}")
        
        # Cleanup
        os.remove(zip_path)
        os.rmdir(download_dir)
        
    except Exception as e:
        await update.message.reply_text(f"Error processing request: {str(e)}")
