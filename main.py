import asyncio
import os
import schedule
import time
import logging
import signal
import sys
from dotenv import load_dotenv
import telegram_bot
import database
import news_analyzer
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Number of news to process at once
NEWS_LIMIT = 2

# Flag to control the scheduler loop
running = True
executor = None
scheduler_future = None

async def check_news():
    """Check for new crypto news, analyze them, and send notifications if important."""
    try:
        logger.info(f"Checking for new crypto news (limit: {NEWS_LIMIT})...")
        important_news = await news_analyzer.fetch_and_process_news(limit=NEWS_LIMIT)
        
        if important_news:
            logger.info(f"Found {len(important_news)} important news items")
            await telegram_bot.send_notifications(important_news)
        else:
            logger.info("No important news found")
            
    except Exception as e:
        logger.error(f"Error checking news: {e}", exc_info=True)

def run_scheduler():
    """Run the scheduler in a separate thread."""
    global running
    logger.info("Scheduler thread started")
    while running:
        schedule.run_pending()
        time.sleep(1)
    logger.info("Scheduler thread stopped")

async def cleanup():
    """Clean up resources before shutting down."""
    global running, executor, scheduler_future
    
    logger.info("Starting cleanup...")
    running = False
    
    # Stop the telegram bot
    try:
        logger.info("Stopping Telegram bot...")
        await telegram_bot.stop_bot()
        logger.info("Telegram bot stopped")
    except Exception as e:
        logger.error(f"Error stopping telegram bot: {e}")
    
    # Shutdown the executor
    if executor:
        logger.info("Shutting down thread executor...")
        try:
            executor.shutdown(wait=False)
            logger.info("Thread executor shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down executor: {e}")
    
    logger.info("Cleanup complete")

async def main():
    """Main function to start the bot and scheduler."""
    global executor, scheduler_future, running
    
    try:
        # Initialize database
        await database.init_db()
        logger.info("Database initialized")
        
        # Schedule news check every 5 minutes
        schedule.every(5).minutes.do(lambda: asyncio.create_task(check_news()))
        logger.info("Scheduled news check every 5 minutes")
        
        # Run initial news check
        await check_news()
        
        # Start the scheduler in a separate thread
        executor = ThreadPoolExecutor(max_workers=1)
        scheduler_future = executor.submit(run_scheduler)
        
        # Start the Telegram bot (this will block until the bot is stopped)
        logger.info("Starting Telegram bot")
        await telegram_bot.start_bot()
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        logger.info("Main function finished, running cleanup")
        await cleanup()

if __name__ == "__main__":
    # Set up proper signal handling for graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Handle signals for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup()))
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        loop.run_until_complete(cleanup())
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        loop.run_until_complete(cleanup())
    finally:
        loop.close()
        logger.info("Application shutdown complete")
