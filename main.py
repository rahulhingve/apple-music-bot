import os
import asyncio
from telegram.ext import Application, CommandHandler
from handlers.start_handler import start_command
from handlers.help_handler import help_command
from handlers.download_handler import alac_command
from database.db_utils import init_db, get_pending_request, cleanup_request
from utils.task_processor import process_download_request

async def process_queue(db_session):
    while True:
        # Get pending request
        request = get_pending_request(db_session)
        if request:
            # Process request
            await process_download_request(request, db_session)
            # Cleanup after processing
            cleanup_request(db_session, request.id)
        await asyncio.sleep(5)  # Wait 5 seconds before checking again

def main():
    # Initialize database
    db_session = init_db()
    
    # Initialize bot with hardcoded token
    app = Application.builder().token(
        ""
    ).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('alac', 
        lambda update, context: alac_command(update, context, db_session)))
    
    # Start task queue processor
    app.job_queue.run_repeating(
        lambda context: process_queue(db_session),
        interval=5
    )
    
    # Start bot
    app.run_polling()

if __name__ == '__main__':
    main()
