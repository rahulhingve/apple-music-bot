import logging
import os
import shutil
from telegram import Bot
from utils.downloader import MusicDownloader
from utils.zip_utils import create_zip
from utils.uploader import upload_to_gofile
from database.db_utils import update_gofile_link
from config import TELEGRAM_BOT_TOKEN, TOOL_PATH

logger = logging.getLogger(__name__)

async def process_download_request(request, db_session):
    """Process a single download request through all tasks sequentially"""
    bot = Bot(TELEGRAM_BOT_TOKEN)
    
    try:
        # Task 1: Download music
        logger.info(f"Task 1: Downloading music for request {request.id}")
        downloader = MusicDownloader(TOOL_PATH)
        download_dir = downloader.download(request.music_url, request.track_numbers)
        if not download_dir:
            raise Exception("Download failed")
        logger.info(f"Download completed to {download_dir}")

        # Task 2: Create ZIP
        logger.info(f"Task 2: Creating ZIP for request {request.id}")
        zip_path = create_zip(download_dir)
        if not zip_path:
            raise Exception("Failed to create ZIP file")
        logger.info(f"ZIP created at {zip_path}")

        # Task 3: Upload to Gofile
        logger.info(f"Task 3: Uploading to Gofile for request {request.id}")
        gofile_url = upload_to_gofile(zip_path)
        if not gofile_url:
            raise Exception("Failed to upload to Gofile")
        logger.info(f"Upload completed: {gofile_url}")

        # Task 4: Update database with link
        logger.info(f"Task 4: Updating database for request {request.id}")
        update_gofile_link(db_session, request.id, gofile_url)

        # Task 5: Send link to user
        logger.info(f"Task 5: Sending link to user {request.user_id}")
        await bot.send_message(
            chat_id=request.user_id,
            text=f"✅ Your download is ready!\n🔗 Download link: https://{gofile_url}"
        )

        # Task 6: Cleanup
        logger.info(f"Task 6: Cleaning up files for request {request.id}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        logger.info("Cleanup completed")

    except Exception as e:
        logger.error(f"Error processing request {request.id}: {str(e)}", exc_info=True)
        try:
            await bot.send_message(
                chat_id=request.user_id,
                text=f"❌ Sorry, there was an error processing your request:\n{str(e)}"
            )
        except:
            logger.error("Failed to send error message to user", exc_info=True)
        raise