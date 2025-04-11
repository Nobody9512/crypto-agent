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
