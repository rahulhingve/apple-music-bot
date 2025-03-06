import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, JobQueue
from handlers.start_handler import start_command
from handlers.help_handler import help_command
from handlers.download_handler import alac_command
from database.db_utils import init_db, get_pending_request, cleanup_request, cleanup_all_requests
from utils.task_processor import process_download_request
from config import TELEGRAM_BOT_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def process_queue(context):
    try:
        db_session = context.application.db_session
        request = get_pending_request(db_session)
        logger.info("Checking queue for pending requests...")
        if request:
            logger.info(f"Processing request {request.id}")
            await process_download_request(request, db_session)
            cleanup_request(db_session, request.id)
            logger.info(f"Completed request {request.id}")
    except Exception as e:
        logger.error(f"Error in queue processing: {str(e)}", exc_info=True)

async def shutdown(application):
    """Cleanup function to run on shutdown"""
    logger.info("Cleaning up before shutdown...")
    try:
        # Clean all database entries
        cleanup_all_requests(application.db_session)
        logger.info("Database cleaned successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def main():
    # Initialize database
    logger.info("Initializing database...")
    db_session = init_db()
    
    # Initialize bot with token from config
    logger.info("Starting bot...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Store db_session in application
    app.db_session = db_session
    
    # Add handlers

    logger.info("Setting up command handlers...")
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('alac', 
        lambda update, context: alac_command(update, context, db_session)))
    
    # Add job queue with error handling
    if app.job_queue:
        logger.info("Starting job queue...")
        job = app.job_queue.run_repeating(process_queue, interval=30, first=10)
        logger.info(f"Job queue started with job {job.name}")
    else:
        logger.error("Failed to initialize job queue!")
    
    # Add shutdown handler
    app.add_handler(CommandHandler('stop', lambda update, context: shutdown(app)))

    try:
        logger.info("Bot is running... Press Ctrl+C to stop")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        # Run cleanup
        asyncio.get_event_loop().run_until_complete(shutdown(app))
        logger.info("Bot stopped cleanly")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
