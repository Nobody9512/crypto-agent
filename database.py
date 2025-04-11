import aiosqlite
import os
from datetime import datetime

DATABASE_NAME = "crypto_news.db"

async def init_db():
    """Initialize the database with required tables."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
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

async def get_important_news(hours=24, min_score=0.7):
    """Get important news from the last N hours with a minimum score."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
        SELECT * FROM news 
        WHERE importance_score >= ? 
        AND datetime(processed_at) >= datetime('now', ?) 
        ORDER BY importance_score DESC
        ''', (min_score, f'-{hours} hours'))
        return await cursor.fetchall() 