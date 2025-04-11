from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import os
import asyncio
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database

# Load environment variables
load_dotenv()

# User ID to send notifications to
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# Bot and dispatcher will be initialized later
bot = None
dp = Dispatcher()

# For stopping the bot
stop_event = asyncio.Event()

async def initialize_bot():
    """Initialize the bot with token from environment variables."""
    global bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables. Check your .env file.")
    bot = Bot(token=token)
    return bot

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """Send a welcome message when the command /start is issued."""
    user_id = message.from_user.id
    await message.answer(f"Salom! Men crypto yangiliklari botiman. Sizning ID: {user_id}")
    
@dp.message(Command("help"))
async def send_help(message: types.Message):
    """Send help information when the command /help is issued."""
    help_text = """
    Men har 5 daqiqada crypto yangiliklari tahlil qilib, muhim yangiliklar haqida xabar beraman.
    
    Mavjud buyruqlar:
    /start - Botni ishga tushirish
    /help - Yordam ko'rsatish
    /latest - Oxirgi muhim yangiliklar
    """
    await message.answer(help_text)

@dp.message(Command("latest"))
async def send_latest_news(message: types.Message):
    """Send the latest important news."""
    news_items = await database.get_important_news(hours=24)
    
    if not news_items:
        await message.answer("Hozirda muhim yangiliklar yo'q.")
        return
    
    for news in news_items:
        await send_news_notification(
            bot,
            message.from_user.id,
            news['title'],
            news['link'],
            news['summary'],
            news['source'],
            news['importance_score'],
            None  # Key points not available from database
        )

async def send_news_notification(bot, user_id, title, link, summary, source, importance_score, key_points=None):
    """Send a notification about important crypto news."""
    importance_emoji = "🔴" if importance_score >= 0.8 else "🟠" if importance_score >= 0.7 else "🟡"
    
    message_text = f"{importance_emoji} <b>{title}</b>\n\n"
    message_text += f"<i>Muhimlik: {importance_score:.2f}/1.0</i>\n"
    message_text += f"Manba: {source}\n\n"
    
    # Add summary (limited length)
    if summary:
        # Limit summary length
        if len(summary) > 200:
            summary = summary[:197] + "..."
        message_text += f"{summary}\n\n"
    
    message_text += f"<a href='{link}'>Batafsil o'qish</a>"
    
    # Create a unique ID for this news item
    import hashlib
    news_id = hashlib.md5(f"{title}:{link}".encode()).hexdigest()[:10]
    
    # Store the news data in the database for later use in callbacks
    await database.save_callback_data(news_id, title, link, summary, source)
    
    # Create inline keyboard with Cancel and Analyze buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel:{news_id}"),
            InlineKeyboardButton(text="📊 Analiz", callback_data=f"analyze:{news_id}")
        ]
    ])
    
    try:
        print(f"Sending notification to user_id: {user_id} (type: {type(user_id)})")
        
        # Ensure user_id is an integer
        if isinstance(user_id, str):
            print(f"Converting user_id from string: '{user_id}' to integer")
            user_id = int(user_id)
        
        # Send message with inline keyboard
        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
            reply_markup=keyboard
        )
        print(f"Successfully sent notification about: {title}")
    except Exception as e:
        print(f"Failed to send notification: {e}")
        print(f"Details - user_id: {user_id}, title: {title}, link: {link}")

# Register callback query handlers for buttons
@dp.callback_query(F.data.startswith("cancel:"))
async def cancel_callback(callback: types.CallbackQuery):
    """Handle cancel button press"""
    # Extract news_id from callback data
    news_id = callback.data.split(":")[1]
    
    # Remove the keyboard
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Answer callback query
    await callback.answer("Bekor qilindi")
    
    # Remove from database
    await database.delete_callback_data(news_id)

@dp.callback_query(F.data.startswith("analyze:"))
async def analyze_callback(callback: types.CallbackQuery):
    """Handle analyze button press"""
    # Extract news_id from callback data
    news_id = callback.data.split(":")[1]
    
    # Answer callback query to show processing
    await callback.answer("Tahlil qilinmoqda...")
    
    # Get news data from database
    news_data = await database.get_callback_data(news_id)
    
    if not news_data:
        await callback.message.reply("Xatolik: Ma'lumot topilmadi.")
        return
    
    # Remove the keyboard from original message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"Error removing keyboard: {e}")
    
    # Perform price impact analysis
    from news_analyzer import analyze_price_impact
    impact_analysis = await analyze_price_impact(news_data['title'], news_data['summary'])
    
    # Send the analysis result
    await callback.message.reply(
        f"<b>💹 Narx ta'siri tahlili:</b>\n\n{impact_analysis}", 
        parse_mode=ParseMode.HTML
    )
    
    # Cleanup after sending analysis (optional)
    # If you want to keep the data for future reference, comment out this line
    # await database.delete_callback_data(news_id)

async def notify_about_important_news(news_items):
    """Send notifications about important news to the specified user."""
    global TELEGRAM_USER_ID
    
    # Check if TELEGRAM_USER_ID is set and valid
    if not TELEGRAM_USER_ID:
        print("Warning: TELEGRAM_USER_ID not set in environment variables")
        return
    
    # Ensure TELEGRAM_USER_ID is an integer
    try:
        user_id = int(TELEGRAM_USER_ID)
    except (ValueError, TypeError):
        print(f"Error: Invalid TELEGRAM_USER_ID format: {TELEGRAM_USER_ID}. Must be a numeric ID.")
        return
    
    print(f"Attempting to send notifications to user ID: {user_id}")
    
    for news in news_items:
        await send_news_notification(
            bot,
            user_id,
            news['title'],
            news['link'],
            news['summary'],
            news['source'],
            news['importance_score'],
            news.get('key_points')
        )

async def start_bot():
    """Start the bot polling."""
    # Initialize bot if not already
    global bot, stop_event
    stop_event.clear()  # Reset the stop event
    
    if bot is None:
        bot = await initialize_bot()
    
    # Clean up old callback data (older than 7 days)
    await database.cleanup_old_callback_data(days=7)
    
    # Starting bot with polling mode
    try:
        # This will run until stop_event is set or a signal is received
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"Error in bot polling: {e}")
    finally:
        if bot:
            # Close bot session
            try:
                await bot.session.close()
            except:
                pass

async def stop_bot():
    """Stop the bot polling."""
    global bot, stop_event
    stop_event.set()  # Set the stop event to terminate polling
    
    try:
        if dp.is_polling():
            print("Stopping bot polling...")
            await dp.stop_polling()
        
        if bot and hasattr(bot, 'session') and not bot.session.closed:
            print("Closing bot session...")
            await bot.session.close()
            
        print("Bot stopped successfully")
    except Exception as e:
        print(f"Error stopping bot: {e}")

# This function will be called from the main.py
async def send_notifications(news_items):
    """Send notifications about news items."""
    # Initialize bot if not already
    global bot
    if bot is None:
        bot = await initialize_bot()
        
    await notify_about_important_news(news_items) 