import aiosqlite
import os
from datetime import datetime

# Get database path from environment variable with fallback to default
DATABASE_NAME = os.getenv("DATABASE_NAME", "crypto_news.db")

# Default value for importance threshold
DEFAULT_IMPORTANCE_THRESHOLD = 0.7

async def init_db():
    """Initialize the database with required tables."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        # News table
        await db.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published TEXT NOT NULL,
            summary TEXT,
            source TEXT NOT NULL,
            importance_score REAL,
            key_points TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Callback cache table for storing news data for callbacks
        await db.execute('''
        CREATE TABLE IF NOT EXISTS callback_cache (
            news_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            summary TEXT,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Settings table for storing bot settings
        await db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Users table for storing bot users
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_admin INTEGER DEFAULT 0,
            balance REAL DEFAULT 0.0,
            language TEXT DEFAULT 'uz',
            notifications INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Initialize settings with default values if they don't exist
        await db.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', ('importance_threshold', str(DEFAULT_IMPORTANCE_THRESHOLD)))
        
        await db.commit()

async def is_news_exists(link):
    """Check if news with given link already exists in the database."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute('SELECT id FROM news WHERE link = ?', (link,))
        result = await cursor.fetchone()
        return result is not None

async def save_news(title, link, published, summary, source, importance_score, key_points=None):
    """Save news item to the database."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('''
        INSERT INTO news (title, link, published, summary, source, importance_score, key_points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, link, published, summary, source, importance_score, key_points))
        await db.commit()

async def get_importance_threshold():
    """Get the current importance threshold from settings."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute('SELECT value FROM settings WHERE key = ?', ('importance_threshold',))
        result = await cursor.fetchone()
        if result:
            try:
                return float(result[0])
            except ValueError:
                return DEFAULT_IMPORTANCE_THRESHOLD
        else:
            # If not found, set the default value and return it
            await db.execute('''
            INSERT INTO settings (key, value) VALUES (?, ?)
            ''', ('importance_threshold', str(DEFAULT_IMPORTANCE_THRESHOLD)))
            await db.commit()
            return DEFAULT_IMPORTANCE_THRESHOLD

async def set_importance_threshold(value):
    """Set a new importance threshold value."""
    try:
        # Ensure value is within valid range 0.0 to 1.0
        value = float(value)
        if value < 0 or value > 1:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute('''
            UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?
            ''', (str(value), 'importance_threshold'))
            await db.commit()
        return True, value
    except ValueError as e:
        return False, str(e)

async def get_important_news(hours=24, min_score=None):
    """Get important news from the last N hours with a minimum score."""
    if min_score is None:
        min_score = await get_importance_threshold()
        
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
        SELECT * FROM news 
        WHERE importance_score >= ? 
        AND datetime(processed_at) >= datetime('now', ?) 
        ORDER BY importance_score DESC
        ''', (min_score, f'-{hours} hours'))
        return await cursor.fetchall()

# New functions for callback cache

async def save_callback_data(news_id, title, link, summary, source):
    """Save news data to callback cache for later use in callbacks."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('''
        INSERT OR REPLACE INTO callback_cache (news_id, title, link, summary, source)
        VALUES (?, ?, ?, ?, ?)
        ''', (news_id, title, link, summary, source))
        await db.commit()

async def get_callback_data(news_id):
    """Get news data from callback cache by news_id."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM callback_cache WHERE news_id = ?', (news_id,))
        result = await cursor.fetchone()
        return dict(result) if result else None

async def delete_callback_data(news_id):
    """Delete news data from callback cache by news_id."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('DELETE FROM callback_cache WHERE news_id = ?', (news_id,))
        await db.commit()

async def cleanup_old_callback_data(days=7):
    """Clean up old callback data that is older than specified days."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('''
        DELETE FROM callback_cache 
        WHERE datetime(created_at) < datetime('now', ?)
        ''', (f'-{days} days',))
        await db.commit() 

async def delete_callback_data(news_id):
    try:
        """Delete news data from callback cache by news_id."""
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute('DELETE FROM callback_cache WHERE news_id = ?', (news_id,))
            await db.commit()
    except Exception as e:
        print(f"Error deleting callback data: {e}")

# User management functions
async def save_user(user_id, username=None, first_name=None, last_name=None, language='uz'):
    """Save a new user or update existing user in the database."""
    try:
        admin_user_id = os.getenv("TELEGRAM_USER_ID")
        is_admin = 1 if str(user_id) == admin_user_id else 0
        
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Check if user exists
            cursor = await db.execute('SELECT user_id, language FROM users WHERE user_id = ?', (user_id,))
            user = await cursor.fetchone()
            
            if user:
                # Don't overwrite existing language setting
                current_language = user[1]
                
                # Update existing user
                await db.execute('''
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, last_active_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''', (username, first_name, last_name, user_id))
            else:
                # Insert new user
                await db.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, is_admin, language, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name, is_admin, language))
            
            await db.commit()
            return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

async def get_all_users():
    """Get all users from the database."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users ORDER BY created_at DESC')
        return await cursor.fetchall()

async def get_user(user_id):
    """Get a user by user_id."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return dict(result) if result else None

async def update_user_balance(user_id, amount):
    """Update user balance, adding or subtracting the specified amount."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute('''
            UPDATE users 
            SET balance = balance + ?, last_active_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            ''', (amount, user_id))
            await db.commit()
            return True
    except Exception as e:
        print(f"Error updating user balance: {e}")
        return False

async def set_user_balance(user_id, new_balance):
    """Set user balance to a specific amount."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute('''
            UPDATE users 
            SET balance = ?, last_active_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            ''', (new_balance, user_id))
            await db.commit()
            return True
    except Exception as e:
        print(f"Error setting user balance: {e}")
        return False

async def count_users():
    """Get the total count of users."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_user_language(user_id):
    """Get the language setting for a user."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 'uz'  # Default to Uzbek if not set

async def set_user_language(user_id, language):
    """Update the language setting for a user."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Check if user exists
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            user = await cursor.fetchone()
            
            if user:
                # Update language for existing user
                await db.execute('''
                UPDATE users 
                SET language = ?, last_active_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''', (language, user_id))
                await db.commit()
                return True
            else:
                # User doesn't exist
                return False
    except Exception as e:
        print(f"Error setting user language: {e}")
        return False

async def get_user_notification_status(user_id):
    """Get the notification status for a user."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute('SELECT notifications FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 1  # Default to enabled if not set

async def set_user_notification_status(user_id, status):
    """Update the notification status for a user."""
    try:
        status_int = 1 if status else 0
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Check if user exists
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            user = await cursor.fetchone()
            
            if user:
                # Update notifications for existing user
                await db.execute('''
                UPDATE users 
                SET notifications = ?, last_active_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''', (status_int, user_id))
                await db.commit()
                return True
            else:
                # User doesn't exist
                return False
    except Exception as e:
        print(f"Error setting user notification status: {e}")
        return False

async def get_users_with_notifications_enabled():
    """Get all users who have notifications enabled."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users WHERE notifications = 1')
        return await cursor.fetchall()

async def charge_user_for_analysis(user_id, amount=0.01):
    """Charge a user for analysis. Returns True if successful, False if balance insufficient."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Get current balance
            cursor = await db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
            
            if not result:
                return False
                
            current_balance = result[0]
            
            # Check if balance is sufficient
            if current_balance < amount:
                return False
                
            # Update balance
            new_balance = current_balance - amount
            await db.execute('''
            UPDATE users 
            SET balance = ?, last_active_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            ''', (new_balance, user_id))
            
            await db.commit()
            return True
    except Exception as e:
        print(f"Error charging user: {e}")
        return False
