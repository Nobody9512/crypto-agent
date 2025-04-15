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
from lang_translate import translations, language_names

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

# States for setting language
class LanguageStates(StatesGroup):
    waiting_for_language = State()

# Create memory storage for FSM
storage = MemoryStorage()

# Bot and dispatcher will be initialized later
bot = None
dp = Dispatcher(storage=storage)

# For stopping the bot
stop_event = asyncio.Event()

async def get_text(key, user_id, **kwargs):
    """Get translated text for a user based on their language preference."""
    language = await database.get_user_language(user_id)
    
    # If language is not available, fall back to Uzbek
    if language not in translations:
        language = 'uz'
    
    text = translations[language].get(key, translations['uz'].get(key, f"Missing translation: {key}"))
    
    # Format with any provided keyword arguments
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError as e:
            print(f"Translation format error for key '{key}': {e}")
            return text
    return text

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
                [KeyboardButton(text=await get_text('btn_stats', user_id)), 
                 KeyboardButton(text=await get_text('btn_users', user_id))],
                [KeyboardButton(text=await get_text('btn_settings', user_id)), 
                 KeyboardButton(text=await get_text('btn_latest', user_id))]
            ],
            resize_keyboard=True
        )
        await message.answer(
            (await get_text('welcome_admin', user_id)).format(user_id=user_id),
            reply_markup=keyboard
        )
    else:
        # Regular user keyboard
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=await get_text('btn_latest', user_id)), 
                 KeyboardButton(text=await get_text('btn_balance', user_id))],
                [KeyboardButton(text=await get_text('btn_help', user_id)),
                 KeyboardButton(text=await get_text('btn_settings', user_id))]
            ],
            resize_keyboard=True
        )
        await message.answer(
            (await get_text('welcome_user', user_id)).format(user_id=user_id),
            reply_markup=keyboard
        )

@dp.message(Command("help"))
async def send_help(message: types.Message):
    """Send help information when the command /help is issued."""
    user_id = message.from_user.id
    help_text = await get_text('help_text', user_id)
    
    # Add admin commands for admin users
    if str(user_id) == TELEGRAM_USER_ID:
        help_text += await get_text('admin_help', user_id)
    
    await message.answer(help_text)

# Command to change language
@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    """Show user settings."""
    user_id = message.from_user.id
    
    # For regular users, just show language settings
    if str(user_id) != TELEGRAM_USER_ID:
        language = await database.get_user_language(user_id)
        language_display = language_names.get(language, language)
        
        # Get notification status
        notification_status = await database.get_user_notification_status(user_id)
        notification_status_text = await get_text('notifications_enabled', user_id) if notification_status else await get_text('notifications_disabled', user_id)
        notification_action = await get_text('notifications_disable', user_id) if notification_status else await get_text('notifications_enable', user_id)
        
        settings_text = await get_text('settings_title', user_id) + "\n\n"
        settings_text += await get_text('settings_language', user_id, language=language_display) + "\n"
        settings_text += await get_text('settings_notifications', user_id, status=notification_status_text)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=await get_text('btn_change_language', user_id), 
                                callback_data="settings:change_language")],
            [InlineKeyboardButton(text=await get_text('btn_change_notifications', user_id, action=notification_action), 
                                callback_data=f"settings:toggle_notifications:{0 if notification_status else 1}")]
        ])
        
        await message.answer(settings_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return
    
    # For admin, show more settings
    threshold = await database.get_importance_threshold()
    language = await database.get_user_language(user_id)
    language_display = language_names.get(language, language)
    
    # Get notification status
    notification_status = await database.get_user_notification_status(user_id)
    notification_status_text = await get_text('notifications_enabled', user_id) if notification_status else await get_text('notifications_disabled', user_id)
    notification_action = await get_text('notifications_disable', user_id) if notification_status else await get_text('notifications_enable', user_id)
    
    settings_text = await get_text('settings_title', user_id) + "\n\n"
    settings_text += await get_text('settings_threshold', user_id, threshold=threshold) + "\n"
    settings_text += await get_text('settings_language', user_id, language=language_display) + "\n"
    settings_text += await get_text('settings_notifications', user_id, status=notification_status_text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await get_text('btn_change_threshold', user_id), 
                            callback_data="admin:set_threshold")],
        [InlineKeyboardButton(text=await get_text('btn_change_language', user_id), 
                            callback_data="settings:change_language")],
        [InlineKeyboardButton(text=await get_text('btn_change_notifications', user_id, action=notification_action), 
                            callback_data=f"settings:toggle_notifications:{0 if notification_status else 1}")]
    ])
    
    await message.answer(settings_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.callback_query(F.data == "settings:change_language")
async def change_language_callback(callback: types.CallbackQuery):
    """Handle change language button press."""
    user_id = callback.from_user.id
    
    # Create language selection buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr")]
    ])
    
    await callback.message.answer(
        await get_text('choose_language', user_id), 
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("lang:"))
async def set_language_callback(callback: types.CallbackQuery):
    """Handle language selection."""
    user_id = callback.from_user.id
    language = callback.data.split(':')[1]
    
    # Update user language in database
    success = await database.set_user_language(user_id, language)
    
    if success:
        # Get language name for display
        language_display = language_names.get(language, language)
        
        # Confirm language change
        await callback.message.answer(
            await get_text('language_set', user_id, language=language_display)
        )
        
        # Show updated settings
        await cmd_settings(callback.message)
        
        # Update main menu buttons according to new language
        if str(user_id) == TELEGRAM_USER_ID:
            # Admin keyboard
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=await get_text('btn_stats', user_id)), 
                     KeyboardButton(text=await get_text('btn_users', user_id))],
                    [KeyboardButton(text=await get_text('btn_settings', user_id)), 
                     KeyboardButton(text=await get_text('btn_latest', user_id))]
                ],
                resize_keyboard=True
            )
            await callback.message.answer(
                (await get_text('welcome_admin', user_id)).format(user_id=user_id),
                reply_markup=keyboard
            )
        else:
            # Regular user keyboard
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=await get_text('btn_latest', user_id)), 
                     KeyboardButton(text=await get_text('btn_balance', user_id))],
                    [KeyboardButton(text=await get_text('btn_help', user_id)),
                     KeyboardButton(text=await get_text('btn_settings', user_id))]
                ],
                resize_keyboard=True
            )
            await callback.message.answer(
                (await get_text('welcome_user', user_id)).format(user_id=user_id),
                reply_markup=keyboard
            )
    
    await callback.answer()

@dp.callback_query(F.data.startswith("settings:toggle_notifications:"))
async def toggle_notifications_callback(callback: types.CallbackQuery):
    """Handle toggle notifications button press."""
    user_id = callback.from_user.id
    new_status = int(callback.data.split(':')[2])
    
    # Update user notification status in database
    success = await database.set_user_notification_status(user_id, new_status)
    
    if success:
        # Show success message
        if new_status:
            await callback.message.answer(await get_text('notifications_enabled_message', user_id))
        else:
            await callback.message.answer(await get_text('notifications_disabled_message', user_id))
        
        # Update settings page
        await cmd_settings(callback.message)
    
    await callback.answer()

# Handle text buttons for command-like functionality
@dp.message(F.text.in_({'ℹ️ Yordam', 'ℹ️ Помощь', 'ℹ️ Help', 'ℹ️ Yardım'}))
async def help_button(message: types.Message):
    await send_help(message)

@dp.message(F.text.in_({'📰 Oxirgi yangiliklar', '📰 Последние новости', '📰 Latest News', '📰 Son haberler'}))
async def latest_news_button(message: types.Message):
    await send_latest_news(message)

@dp.message(F.text.in_({'💰 Balans', '💰 Баланс', '💰 Balance', '💰 Bakiye'}))
async def balance_button(message: types.Message):
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    
    if user:
        await message.answer(await get_text('balance', user_id, balance=user['balance']))
    else:
        await message.answer(await get_text('not_registered', user_id))

@dp.message(F.text.in_({'⚙️ Sozlamalar', '⚙️ Настройки', '⚙️ Settings', '⚙️ Ayarlar'}))
async def settings_button(message: types.Message):
    await cmd_settings(message)

# Admin panel buttons
@dp.message(F.text.in_({'📊 Statistika', '📊 Статистика', '📊 Statistics', '📊 İstatistikler'}))
async def stats_button(message: types.Message):
    # Check if the user is admin
    user_id = message.from_user.id
    if str(user_id) != TELEGRAM_USER_ID:
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
    
    stats_text = f"\n{await get_text('stats_title', user_id)}\n\n"
    stats_text += await get_text('stats_users', user_id, count=total_users) + "\n"
    stats_text += await get_text('stats_news', user_id, count=total_news) + "\n"
    stats_text += await get_text('stats_important', user_id, threshold=threshold, count=important_news)
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

@dp.message(F.text.in_({'👥 Foydalanuvchilar', '👥 Пользователи', '👥 Users', '👥 Kullanıcılar'}))
async def users_button(message: types.Message):
    # Check if the user is admin
    user_id = message.from_user.id
    if str(user_id) != TELEGRAM_USER_ID:
        return
    
    # Get all users
    users = await database.get_all_users()
    
    if not users:
        await message.answer(await get_text('no_users', user_id))
        return
    
    # Prepare users list
    users_text = f"<b>{await get_text('users_title', user_id)}</b>\n\n"
    
    for i, user in enumerate(users, 1):
        user_id_in_list = user['user_id']
        username = user['username'] or await get_text('username_none', user_id)
        name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or await get_text('name_none', user_id)
        admin_status = await get_text('user_admin', user_id) if user['is_admin'] else await get_text('user_regular', user_id)
        balance = user['balance']
        language = user['language']
        language_display = language_names.get(language, language)
        
        users_text += f"{i}. {admin_status} | {name} (@{username})\n"
        users_text += f"   ID: {user_id_in_list} | {await get_text('settings_language', user_id, language=language_display)}\n"
        users_text += f"   {await get_text('balance', user_id, balance=balance)}\n\n"
    
    # Add management options
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await get_text('btn_add_balance', user_id), callback_data="admin:add_balance")],
        [InlineKeyboardButton(text=await get_text('btn_refresh', user_id), callback_data="admin:refresh_users")]
    ])
    
    await message.answer(users_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.message(Command("latest"))
async def send_latest_news(message: types.Message):
    """Send the latest important news."""
    news_items = await database.get_important_news(hours=24)
    
    if not news_items:
        await message.answer(await get_text('no_news', message.from_user.id))
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
        await message.answer(await get_text('admin_only', message.from_user.id))
        return
    
    # Get current threshold
    current_threshold = await database.get_importance_threshold()
    
    await message.answer(
        await get_text('threshold_current', message.from_user.id, threshold=current_threshold)
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
            await get_text('threshold_updated', message.from_user.id, threshold=result)
        )
    else:
        await message.answer(
            await get_text('threshold_error', message.from_user.id, error=result)
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
    
    await message.answer(await get_text('enter_user_id', message.from_user.id))
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
        await message.answer(await get_text('cancel_balance', message.from_user.id))
        await state.clear()
        return
    
    try:
        user_id = int(text)
        user = await database.get_user(user_id)
        
        if not user:
            await message.answer(await get_text('user_not_found', message.from_user.id))
            return
        
        # Store user_id in state
        await state.update_data(user_id=user_id)
        
        # Show user info
        username = user['username'] or await get_text('username_none', message.from_user.id)
        name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or await get_text('name_none', message.from_user.id)
        
        await message.answer(
            await get_text('user_info', message.from_user.id, name=name, username=username, balance=user['balance'])
        )
        
        await state.set_state(BalanceStates.waiting_for_amount)
    except ValueError:
        await message.answer(await get_text('invalid_user_id', message.from_user.id))

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
        await message.answer(await get_text('cancel_balance', message.from_user.id))
        await state.clear()
        return
    
    try:
        amount = float(text)
        
        # Get user_id from state
        data = await state.get_data()
        user_id = data.get('user_id')
        
        if not user_id:
            await message.answer(await get_text('no_action', message.from_user.id))
            await state.clear()
            return
        
        # Update user balance
        success = await database.set_user_balance(user_id, amount)
        
        if success:
            # Get updated user info
            user = await database.get_user(user_id)
            username = user['username'] or await get_text('username_none', message.from_user.id)
            name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or await get_text('name_none', message.from_user.id)
            
            await message.answer(
                await get_text('balance_updated', message.from_user.id, name=name, username=username, balance=user['balance'])
            )
        else:
            await message.answer(await get_text('balance_error', message.from_user.id))
        
        await state.clear()
    except ValueError:
        await message.answer(await get_text('invalid_amount', message.from_user.id))

# Handle cancel command for all states
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Cancel current operation."""
    current_state = await state.get_state()
    
    if current_state is not None:
        await message.answer(await get_text('cancel_command', message.from_user.id))
        await state.clear()
    else:
        await message.answer(await get_text('no_action', message.from_user.id))

# Admin callback handlers
@dp.callback_query(F.data.startswith("admin:"))
async def admin_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handle admin callbacks."""
    # Check if the user is admin
    if str(callback.from_user.id) != TELEGRAM_USER_ID:
        await callback.answer(await get_text('admin_only', callback.from_user.id))
        return
    
    action = callback.data.split(":")[1]
    
    if action == "refresh_users":
        await callback.answer(await get_text('btn_refresh', callback.from_user.id))
        await users_button(callback.message)
    
    elif action == "add_balance":
        await callback.answer(await get_text('btn_add_balance', callback.from_user.id))
        await callback.message.answer(await get_text('enter_user_id', callback.from_user.id))
        await state.set_state(BalanceStates.waiting_for_user_id)
    
    elif action == "set_threshold":
        await callback.answer(await get_text('btn_change_threshold', callback.from_user.id))
        current_threshold = await database.get_importance_threshold()
        
        await callback.message.answer(
            await get_text('threshold_current', callback.from_user.id, threshold=current_threshold)
        )
        
        await state.set_state(ThresholdStates.waiting_for_threshold)

async def send_news_notification(bot, user_id, title, link, summary, source, importance_score, key_points=None):
    """Send a notification about important crypto news."""
    # Get user language
    language = await database.get_user_language(user_id)
    
    # Determine importance emoji
    importance_emoji = "🔴" if importance_score >= 0.8 else "🟠" if importance_score >= 0.7 else "🟡"
    
    # Get translated texts
    importance_text = translations[language].get('importance', "Muhimlik: {importance}/1.0")
    source_text = translations[language].get('source', "Manba: {source}")
    read_more_text = translations[language].get('read_more', "Batafsil o'qish")
    
    # Build message
    message_text = f"{importance_emoji} <b>{title}</b>\n\n"
    message_text += f"<i>{importance_text.format(importance=f'{importance_score:.2f}')}</i>\n"
    message_text += f"{source_text.format(source=source)}\n\n"
    
    # Add summary (limited length)
    if summary:
        # Limit summary length
        if len(summary) > 200:
            summary = summary[:197] + "..."
        message_text += f"{summary}\n\n"
    
    message_text += f"<a href='{link}'>{read_more_text}</a>"
    
    # Create a unique ID for this news item
    import hashlib
    news_id = hashlib.md5(f"{title}:{link}".encode()).hexdigest()[:10]
    
    # Store the news data in the database for later use in callbacks
    await database.save_callback_data(news_id, title, link, summary, source)
    
    # Get button text translations
    cancel_btn_text = translations[language].get('btn_cancel', "❌ Cancel")
    analyze_btn_text = translations[language].get('btn_analyze', "📊 Analiz")
    
    # Create inline keyboard with Cancel and Analyze buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cancel_btn_text, callback_data=f"cancel:{news_id}"),
            InlineKeyboardButton(text=analyze_btn_text, callback_data=f"analyze:{news_id}")
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
    user_id = callback.from_user.id
    
    # Extract news_id from callback data
    news_id = callback.data.split(":")[1]
    
    # Remove the keyboard
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Answer callback query
    await callback.answer(await get_text('cancel_news', user_id))
    
    # Remove from database
    await database.delete_callback_data(news_id)

@dp.callback_query(F.data.startswith("analyze:"))
async def analyze_callback(callback: types.CallbackQuery):
    """Handle analyze button press"""
    user_id = callback.from_user.id
    
    # Extract news_id from callback data
    news_id = callback.data.split(":")[1]
    
    # Check user balance first
    user = await database.get_user(user_id)
    if not user or user['balance'] < 0.01:
        # Insufficient balance
        await callback.answer()
        await callback.message.reply(
            await get_text('insufficient_balance', user_id, balance=user['balance'] if user else 0)
        )
        return
    
    # Answer callback query to show processing
    await callback.answer(await get_text('analyzing', user_id))
    
    # Get news data from database
    news_data = await database.get_callback_data(news_id)
    
    if not news_data:
        await callback.message.reply(await get_text('error_data_not_found', user_id))
        return
    
    # Remove the keyboard from original message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"Error removing keyboard: {e}")
    
    # Charge user for analysis
    success = await database.charge_user_for_analysis(user_id)
    if not success:
        # Double-check balance (in case it changed between checks)
        await callback.message.reply(
            await get_text('insufficient_balance', user_id, balance=(await database.get_user(user_id))['balance'])
        )
        return
    
    # Get user language
    language = await database.get_user_language(user_id)
    
    # Perform price impact analysis with user's language
    from news_analyzer import analyze_price_impact
    impact_analysis = await analyze_price_impact(news_data['title'], news_data['summary'], language)
    
    # Send the analysis result with fee note
    analysis_text = await get_text('analysis_fee', user_id)
    analysis_text += f"<b>{await get_text('price_impact_analysis', user_id)}</b>\n\n{impact_analysis}"
    
    await callback.message.reply(
        analysis_text, 
        parse_mode=ParseMode.HTML
    )
    
    # Cleanup after sending analysis (optional)
    # If you want to keep the data for future reference, comment out this line
    await database.delete_callback_data(news_id)

async def notify_about_important_news(news_items):
    """Send notifications about important news to users who have enabled notifications."""
    # Get all users with notifications enabled
    users = await database.get_users_with_notifications_enabled()
    
    if not users:
        print("No users have notifications enabled.")
        return
    
    print(f"Attempting to send notifications to {len(users)} users")
    
    for user in users:
        user_id = user['user_id']
        
        for news in news_items:
            try:
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
            except Exception as e:
                print(f"Error sending notification to user {user_id}: {e}")
                continue

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