import asyncio
import logging
import signal
from dotenv import load_dotenv
import telegram_bot
import database
import news_analyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

NEWS_LIMIT = 2
running = True

async def check_news():
    """Yangi kripto xabarlarini tekshiradi va xabar yuboradi."""
    try:
        logger.info(f"Checking for new crypto news (limit: {NEWS_LIMIT})...")
        important_news = await news_analyzer.fetch_and_process_news(limit=NEWS_LIMIT)

        if important_news:
            logger.info(f"Found {len(important_news)} important news items.")
            await telegram_bot.send_notifications(important_news)
        else:
            logger.info("No important news found.")

    except Exception as e:
        logger.error(f"Error checking news: {e}", exc_info=True)

async def scheduler():
    """Har 5 daqiqada bir marta xabarlarni tekshiradi."""
    while running:
        await check_news()
        await asyncio.sleep(60)  # 300 soniya = 5 daqiqa

async def cleanup():
    """Botni toʻxtatishdan oldin resurslarni tozalaydi."""
    global running
    running = False

    try:
        logger.info("Stopping Telegram bot...")
        await telegram_bot.stop_bot()
        logger.info("Telegram bot stopped.")
    except Exception as e:
        logger.error(f"Error stopping Telegram bot: {e}")

    logger.info("Cleanup completed.")

async def main():
    """Dasturga kirish nuqtasi."""
    global running

    await database.init_db()
    logger.info("Database initialized.")

    scheduler_task = asyncio.create_task(scheduler())

    try:
        logger.info("Starting Telegram bot...")
        await telegram_bot.start_bot()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}", exc_info=True)
    finally:
        logger.info("Main function finished, starting cleanup...")
        await cleanup()
        scheduler_task.cancel()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup()))

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        loop.run_until_complete(cleanup())
    finally:
        loop.close()
        logger.info("Application shutdown complete.")
