from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
import asyncio
import aiosqlite
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import database

# Load environment variables
load_dotenv()

# User ID to send notifications to
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# States for setting threshold
class ThresholdStates(StatesGroup):
    waiting_for_threshold = State()

# States for setting user balance
class BalanceStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()

# Create memory storage for FSM
storage = MemoryStorage()

# Bot and dispatcher will be initialized later
bot = None
dp = Dispatcher(storage=storage)

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
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Save user to database
    await database.save_user(user_id, username, first_name, last_name)
    
    # Create different UI for admin vs regular users
    if str(user_id) == TELEGRAM_USER_ID:
        # Admin keyboard
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Foydalanuvchilar")],
                [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="📰 Oxirgi yangiliklar")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Salom, Admin! Men crypto yangiliklari botiman. "
            f"Sizning ID: {user_id}",
            reply_markup=keyboard
        )
    else:
        # Regular user keyboard
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📰 Oxirgi yangiliklar"), KeyboardButton(text="💰 Balans")],
                [KeyboardButton(text="ℹ️ Yordam")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Salom! Men crypto yangiliklari botiman. "
            f"Sizning ID: {user_id}",
            reply_markup=keyboard
        )
    
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
    
    # Add admin commands for admin users
    if str(message.from_user.id) == TELEGRAM_USER_ID:
        help_text += """
    Admin buyruqlari:
    /current_threshold - Hozirgi muhimlik darajasini ko'rsatish
    /threshold - Muhimlik darajasini o'zgartirish (0.0-1.0)
    /users - Foydalanuvchilar ro'yxati
    /stats - Bot statistikasi
    /set_balance - Foydalanuvchi balansini o'zgartirish
        """
    
    await message.answer(help_text)

# Handle text buttons for command-like functionality
@dp.message(F.text == "ℹ️ Yordam")
async def help_button(message: types.Message):
    await send_help(message)

@dp.message(F.text == "📰 Oxirgi yangiliklar")
async def latest_news_button(message: types.Message):
    await send_latest_news(message)

@dp.message(F.text == "💰 Balans")
async def balance_button(message: types.Message):
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    
    if user:
        await message.answer(f"Sizning balans: {user['balance']} USDT")
    else:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start buyrug'ini yuborib ro'yxatdan o'ting.")

# Admin panel buttons
@dp.message(F.text == "📊 Statistika")
async def stats_button(message: types.Message):
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    # Get statistics
    total_users = await database.count_users()
    threshold = await database.get_importance_threshold()
    
    # Get news count from the last 24 hours
    async with aiosqlite.connect(database.DATABASE_NAME) as db:
        cursor = await db.execute('''
        SELECT COUNT(*) FROM news 
        WHERE datetime(processed_at) >= datetime('now', '-24 hours')
        ''')
        total_news = (await cursor.fetchone())[0]
        
        cursor = await db.execute('''
        SELECT COUNT(*) FROM news 
        WHERE importance_score >= ? AND datetime(processed_at) >= datetime('now', '-24 hours')
        ''', (threshold,))
        important_news = (await cursor.fetchone())[0]
    
    stats_text = f"""
📊 <b>Bot Statistikasi</b>

👥 Foydalanuvchilar soni: {total_users}
📰 So'nggi 24 soat ichidagi yangiliklar: {total_news}
🔔 Muhim yangiliklar (score >= {threshold:.2f}): {important_news}
    """
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "👥 Foydalanuvchilar")
async def users_button(message: types.Message):
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    # Get all users
    users = await database.get_all_users()
    
    if not users:
        await message.answer("Hozircha foydalanuvchilar yo'q.")
        return
    
    # Prepare users list
    users_text = "<b>👥 Foydalanuvchilar ro'yxati:</b>\n\n"
    
    for i, user in enumerate(users, 1):
        username = user['username'] or "username yo'q"
        name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or "ism yo'q"
        admin_status = "👑 Admin" if user['is_admin'] else "👤 Foydalanuvchi"
        balance = user['balance']
        
        users_text += f"{i}. {admin_status} | {name} (@{username})\n"
        users_text += f"   ID: {user['user_id']} | Balans: {balance} USDT\n\n"
    
    # Add management options
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Balans qo'shish", callback_data="admin:add_balance")],
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin:refresh_users")]
    ])
    
    await message.answer(users_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.message(F.text == "⚙️ Sozlamalar")
async def settings_button(message: types.Message):
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    # Get current threshold
    threshold = await database.get_importance_threshold()
    
    settings_text = f"""
⚙️ <b>Bot Sozlamalari</b>

🔢 Muhimlik darajasi: {threshold:.2f}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 Muhimlik darajasini o'zgartirish", callback_data="admin:set_threshold")]
    ])
    
    await message.answer(settings_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

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

@dp.message(Command("threshold"))
async def cmd_threshold(message: types.Message, state: FSMContext):
    """Command to change the importance threshold."""
    # Check if the user is authorized
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        await message.answer("Bu buyruqni faqat bot egasi ishlatishi mumkin.")
        return
    
    # Get current threshold
    current_threshold = await database.get_importance_threshold()
    
    await message.answer(
        f"Hozirgi muhimlik darajasi: {current_threshold:.2f}\n\n"
        f"Yangi qiymatni kiriting (0.0-1.0 oralig'ida):"
    )
    
    # Set the state to waiting for threshold
    await state.set_state(ThresholdStates.waiting_for_threshold)

@dp.message(ThresholdStates.waiting_for_threshold)
async def process_threshold(message: types.Message, state: FSMContext):
    """Process the threshold value entered by the user."""
    # Check if the user is authorized
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        await state.clear()
        return
    
    # Get the threshold value from the message
    threshold_str = message.text.strip()
    
    # Try to set the new threshold value
    success, result = await database.set_importance_threshold(threshold_str)
    
    if success:
        await message.answer(
            f"✅ Muhimlik darajasi muvaffaqiyatli o'zgartirildi: {result:.2f}"
        )
    else:
        await message.answer(
            f"❌ Xato: {result}\n\n"
            f"Iltimos, 0.0 dan 1.0 gacha bo'lgan son kiriting."
        )
    
    # Clear the state
    await state.clear()

@dp.message(Command("current_threshold"))
async def cmd_current_threshold(message: types.Message):
    """Show the current importance threshold."""
    # Check if the user is authorized
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    # Get current threshold
    current_threshold = await database.get_importance_threshold()
    
    # Explain what different threshold values mean
    explanation = f"""
<b>Hozirgi muhimlik darajasi:</b> {current_threshold:.2f}

<i>Muhimlik darajasi qiymatlari:</i>
• 0.1-0.3: Juda past (deyarli barcha yangiliklar)
• 0.3-0.5: Past (ko'p yangiliklar)
• 0.5-0.7: O'rta (muhim yangiliklar)
• 0.7-0.8: Yuqori (juda muhim yangiliklar)
• 0.8-1.0: Juda yuqori (eng muhim yangiliklar)

Muhimlik darajasini o'zgartirish uchun /threshold buyrug'ini ishlating.
    """
    
    await message.answer(explanation, parse_mode=ParseMode.HTML)

# Admin command for listing users
@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    """List all users."""
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    await users_button(message)

# Admin command for stats
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Show bot statistics."""
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    await stats_button(message)

# Admin command for setting user balance
@dp.message(Command("set_balance"))
async def cmd_set_balance(message: types.Message, state: FSMContext):
    """Set user balance."""
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        return
    
    await message.answer("Foydalanuvchi ID raqamini kiriting:")
    await state.set_state(BalanceStates.waiting_for_user_id)

@dp.message(BalanceStates.waiting_for_user_id)
async def process_balance_user_id(message: types.Message, state: FSMContext):
    """Process user ID for balance update."""
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        await state.clear()
        return
    
    text = message.text.strip()
    
    # Check if this is a cancel request
    if text.lower() in ['/cancel', 'cancel', 'bekor', 'bekor qilish', 'orqaga']:
        await message.answer("🛑 Balans o'zgartirish amaliyoti bekor qilindi.")
        await state.clear()
        return
    
    try:
        user_id = int(text)
        user = await database.get_user(user_id)
        
        if not user:
            await message.answer("❌ Bunday foydalanuvchi topilmadi. Qaytadan urinib ko'ring yoki bekor qilish uchun /cancel buyrug'ini yuboring.")
            return
        
        # Store user_id in state
        await state.update_data(user_id=user_id)
        
        # Show user info
        username = user['username'] or "username yo'q"
        name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or "ism yo'q"
        
        await message.answer(
            f"Foydalanuvchi: {name} (@{username})\n"
            f"Hozirgi balans: {user['balance']} USDT\n\n"
            f"Yangi balans qiymatini kiriting yoki bekor qilish uchun /cancel buyrug'ini yuboring:"
        )
        
        await state.set_state(BalanceStates.waiting_for_amount)
    except ValueError:
        await message.answer("❌ Xato: Foydalanuvchi ID raqami butun son bo'lishi kerak. Bekor qilish uchun /cancel buyrug'ini yuboring.")

@dp.message(BalanceStates.waiting_for_amount)
async def process_balance_amount(message: types.Message, state: FSMContext):
    """Process amount for balance update."""
    # Check if the user is admin
    if str(message.from_user.id) != TELEGRAM_USER_ID:
        await state.clear()
        return
    
    text = message.text.strip()
    
    # Check if this is a cancel request
    if text.lower() in ['/cancel', 'cancel', 'bekor', 'bekor qilish', 'orqaga']:
        await message.answer("🛑 Balans o'zgartirish amaliyoti bekor qilindi.")
        await state.clear()
        return
    
    try:
        amount = float(text)
        
        # Get user_id from state
        data = await state.get_data()
        user_id = data.get('user_id')
        
        if not user_id:
            await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
            await state.clear()
            return
        
        # Update user balance
        success = await database.set_user_balance(user_id, amount)
        
        if success:
            # Get updated user info
            user = await database.get_user(user_id)
            username = user['username'] or "username yo'q"
            name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or "ism yo'q"
            
            await message.answer(
                f"✅ Foydalanuvchi balansi muvaffaqiyatli yangilandi:\n\n"
                f"Foydalanuvchi: {name} (@{username})\n"
                f"Yangi balans: {user['balance']} USDT"
            )
        else:
            await message.answer("❌ Balansni yangilashda xatolik yuz berdi. Qaytadan urinib ko'ring.")
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Xato: Balans son bo'lishi kerak. Bekor qilish uchun /cancel buyrug'ini yuboring.")

# Handle cancel command for all states
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Cancel current operation."""
    current_state = await state.get_state()
    
    if current_state is not None:
        await message.answer("🛑 Amal bekor qilindi.")
        await state.clear()
    else:
        await message.answer("⚠️ Hech qanday amal bajarilmayapti.")

# Admin callback handlers
@dp.callback_query(F.data.startswith("admin:"))
async def admin_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handle admin callbacks."""
    # Check if the user is admin
    if str(callback.from_user.id) != TELEGRAM_USER_ID:
        await callback.answer("Bu amal faqat admin uchun.")
        return
    
    action = callback.data.split(":")[1]
    
    if action == "refresh_users":
        await callback.answer("Foydalanuvchilar ro'yxati yangilanmoqda...")
        await users_button(callback.message)
    
    elif action == "add_balance":
        await callback.answer("Balans qo'shish...")
        await callback.message.answer("Foydalanuvchi ID raqamini kiriting:")
        await state.set_state(BalanceStates.waiting_for_user_id)
    
    elif action == "set_threshold":
        await callback.answer("Muhimlik darajasini o'zgartirish...")
        current_threshold = await database.get_importance_threshold()
        
        await callback.message.answer(
            f"Hozirgi muhimlik darajasi: {current_threshold:.2f}\n\n"
            f"Yangi qiymatni kiriting (0.0-1.0 oralig'ida):"
        )
        
        await state.set_state(ThresholdStates.waiting_for_threshold)

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
    await database.delete_callback_data(news_id)

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