import os
import asyncio
import logging
from telegram import Update  # Add this import
from telegram.ext import Application, CommandHandler, JobQueue
from handlers.start_handler import start_command
from handlers.help_handler import help_command
from handlers.download_handler import alac_command
from database.db_utils import init_db, get_pending_request, cleanup_request
from utils.task_processor import process_download_request

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def process_queue(context):
    db_session = context.application.db_session
    request = get_pending_request(db_session)
    logger.info("Checking queue for pending requests...")
    if request:
        await process_download_request(request, db_session)
        cleanup_request(db_session, request.id)

def main():
    # Initialize database
    logger.info("Initializing database...")
    db_session = init_db()
    
    # Initialize bot with hardcoded token
    logger.info("Starting bot...")
    app = Application.builder().token(
        "7804911748:AAH9rPMlyfYNnJtRdXLkotT8ToC8eoCEbPI"
    ).build()
    
    # Store db_session in application
    app.db_session = db_session
    
    # Add handlers

    logger.info("Setting up command handlers...")
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('alac', 
        lambda update, context: alac_command(update, context, db_session)))
    
    # Add job queue
    if app.job_queue:
        logger.info("Starting job queue...")
        app.job_queue.run_repeating(process_queue, interval=5)
    
    # Start bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
