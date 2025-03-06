
import os
from telegram import Bot
from utils.downloader import MusicDownloader
from utils.zip_utils import create_zip
from utils.uploader import upload_to_gofile

async def process_download_request(request, db_session):
    bot = Bot("7804911748:AAH9rPMlyfYNnJtRdXLkotT8ToC8eoCEbPI")
    
    try:
        # Task 1: Download
        downloader = MusicDownloader("/root/apple-music-alac-atmos-downloader")
        download_dir = downloader.download(request.music_url, request.track_numbers)
        
        # Task 2: Create ZIP
        zip_path = create_zip(download_dir)
        if not zip_path:
            raise Exception("Failed to create ZIP file")
        
        # Task 3: Upload to Gofile
        gofile_url = upload_to_gofile(zip_path)
        if not gofile_url:
            raise Exception("Failed to upload to Gofile")
        
        # Task 4: Send link to user
        await bot.send_message(
            chat_id=request.user_id,
            text=f"Your download is ready: https://{gofile_url}"
        )
        
        # Task 5: Cleanup
        os.remove(zip_path)
        if os.path.exists(download_dir):
            for root, dirs, files in os.walk(download_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(download_dir)
            
    except Exception as e:
        await bot.send_message(
            chat_id=request.user_id,
            text=f"Error processing your request: {str(e)}"
        )
        raise