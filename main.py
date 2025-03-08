import os
import signal
import asyncio
import logging
import tempfile
import psutil
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

# Global flag for shutdown
is_shutting_down = False

LOCK_FILE = os.path.join(tempfile.gettempdir(), 'telegram_music_bot.lock')

def is_bot_running():
    """Check if another instance is running"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            # Check if process exists and is a python process
            process = psutil.Process(old_pid)
            if process.name().startswith('python'):
                cmdline = ' '.join(process.cmdline())
                if 'main.py' in cmdline:
                    return True
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
    return False

def create_lock_file():
    """Create lock file with current PID"""
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def remove_lock_file():
    """Remove lock file"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass

def signal_handler(signum, frame):
    global is_shutting_down
    logger.info(f"Received signal {signum}")
    is_shutting_down = True

async def process_queue(context):
    global is_shutting_down
    if is_shutting_down:
        return
        
    try:
        db_session = context.application.db_session
        request = get_pending_request(db_session)
        logger.info("Checking queue for pending requests...")
        if request:
            logger.info(f"Processing request {request.id}")
            await process_download_request(request, db_session)
            cleanup_request(db_session, request.id)
            logger.info(f"Completed request {request.id}")
        db_session.remove()  # Release session after use
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
    # Check if bot is already running
    if is_bot_running():
        logger.error("Bot is already running! Exiting.")
        return

    # Create lock file
    create_lock_file()

    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initialize database with connection pooling
        logger.info("Initializing database...")
        db_session = init_db(pooling=True)
        
        # Initialize bot with more conservative settings
        logger.info("Starting bot...")
        app = (Application.builder()
               .token(TELEGRAM_BOT_TOKEN)
               .read_timeout(30)
               .write_timeout(30)
               .pool_timeout(30)
               .connect_timeout(30)
               .build())
        
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
            job = app.job_queue.run_repeating(
                process_queue, 
                interval=60,  # Increased interval to reduce CPU usage
                first=10,
                name='queue_processor'
            )
            logger.info(f"Job queue started with job {job.name}")
        else:
            logger.error("Failed to initialize job queue!")
        
        # Add shutdown handler
        app.add_handler(CommandHandler('stop', lambda update, context: shutdown(app)))

        try:
            logger.info("Bot is running... Press Ctrl+C to stop")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                stop_signals=(signal.SIGINT, signal.SIGTERM)
            )
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            try:
                # Create new event loop for cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(shutdown(app))
                loop.close()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
            logger.info("Bot stopped cleanly")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
    finally:
        remove_lock_file()
        logger.info("Cleaned up lock file")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        remove_lock_file()
        logger.info("Shutting down...")
