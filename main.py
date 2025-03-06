import os
import asyncio
from telegram.ext import Application, CommandHandler, JobQueue
from handlers.start_handler import start_command
from handlers.help_handler import help_command
from handlers.download_handler import alac_command
from database.db_utils import init_db, get_pending_request, cleanup_request
from utils.task_processor import process_download_request

async def process_queue(context):
    db_session = context.application.db_session
    request = get_pending_request(db_session)
    if request:
        await process_download_request(request, db_session)
        cleanup_request(db_session, request.id)

def main():
    # Initialize database
    db_session = init_db()
    
    # Initialize bot with hardcoded token
    app = Application.builder().token(
        ""
    ).build()
    
    # Store db_session in application
    app.db_session = db_session
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('alac', 
        lambda update, context: alac_command(update, context, db_session)))
    
    # Add job queue
    if app.job_queue:
        app.job_queue.run_repeating(process_queue, interval=5)
    
    #
