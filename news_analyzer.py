import feedparser
import asyncio
import openai
from openai import OpenAI
import os
from datetime import datetime
import database
from lang_translate import format_instructions, language_instructions

# RSS feed sources
RSS_SOURCES = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss",
    "CoinTelegraph": "https://cointelegraph.com/rss"
}

# Get OpenAI model from environment variable with fallback
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")

async def fetch_rss_feeds(limit=5):
    """
    Fetch news from all RSS sources.
    
    Args:
        limit (int): Maximum number of new entries to process
    """
    all_entries = []
    new_entries_count = 0
    
    for source, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            
            # Sort entries by published date (newest first)
            if feed.entries and hasattr(feed.entries[0], 'published_parsed'):
                feed.entries.sort(key=lambda x: x.published_parsed if hasattr(x, 'published_parsed') else 0, reverse=True)
            
            for entry in feed.entries:
                # Check if we've already reached the limit
                if new_entries_count >= limit:
                    break
                    
                # Add source information to each entry
                entry['source'] = source
                
                # Check if entry already exists in database
                if not await database.is_news_exists(entry.get('link', '')):
                    all_entries.append(entry)
                    new_entries_count += 1
                    
                    # Break if we've reached the limit
                    if new_entries_count >= limit:
                        break
                        
        except Exception as e:
            print(f"Error fetching RSS from {source}: {e}")
    
    print(f"Found {new_entries_count} new news entries to process")
    return all_entries

async def analyze_news_importance(title, summary):
    """
    Analyze news importance using OpenAI to determine if it could impact crypto prices.
    Returns a score between 0 and 1 where higher values indicate more importance.
    """
    prompt = f"""
    Analyze the following cryptocurrency news and rate its potential impact on crypto prices on a scale of 0 to 1.
    Consider factors like regulatory changes, major adoption news, market events, security issues, etc.
    
    Title: {title}
    Summary: {summary}
    
    Return only a numeric score between 0 and 1, where:
    - 0 to 0.3: Low impact, routine news with little price effect
    - 0.3 to 0.7: Moderate impact, may cause some market movement
    - 0.7 to 1.0: High impact, likely to cause significant price changes
    
    Score:
    """
    
    try:
        # Create client with new API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a cryptocurrency market analyst who evaluates news impact on crypto prices. Only respond with a numeric score between 0 and 1."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        
        # Get score from new API structure
        score_text = response.choices[0].message.content.strip()
        
        # Extract the numeric score
        try:
            score = float(score_text)
            # Ensure the score is between 0 and 1
            score = max(0, min(score, 1))
            return score
        except ValueError:
            # If we can't extract a valid score, assume moderate importance
            return 0.5
    except Exception as e:
        print(f"Error analyzing news importance: {e}")
        # Default to moderate importance on error
        return 0.5

async def analyze_price_impact(title, summary, language='uz'):
    """
    Analyze how the news could impact cryptocurrency prices for BTC, ETH, SOL, and LTC.
    Returns a detailed analysis of potential price movements.
    
    Args:
        title (str): The news title
        summary (str): The news summary
        language (str): Language code (uz, ru, en, tr)
    """
    
    # Fallback to Uzbek if language not supported
    if language not in language_instructions:
        language = 'uz'
    
    prompt = f"""
    Analyze the following cryptocurrency news and predict its potential impact on the prices of:
    1. Bitcoin (BTC)
    2. Ethereum (ETH)
    3. Solana (SOL)
    4. Litecoin (LTC)
    
    For each cryptocurrency, predict whether the price might:
    - 📈 Go up (positive impact)
    - 📉 Go down (negative impact)
    - ➡️ Remain stable (neutral impact)
    
    Consider regulatory news, adoption news, market sentiment, technical developments, etc.
    
    Title: {title}
    Summary: {summary}
    
    {language_instructions[language]}
    {format_instructions[language]}
    """
    
    try:
        # Create client with new API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a cryptocurrency market analyst who predicts price movements based on news."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        # Get analysis from API response
        analysis = response.choices[0].message.content.strip()
        return analysis
    except Exception as e:
        print(f"Error analyzing price impact: {e}")
        # Return error message in the requested language
        error_messages = {
            'uz': "⚠️ Tahlil qilishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
            'ru': "⚠️ Произошла ошибка при анализе. Пожалуйста, повторите попытку позже.",
            'en': "⚠️ Error analyzing the impact. Please try again later.",
            'tr': "⚠️ Hata analizinde. Lütfen daha sonra tekrar deneyin."
        }
        return error_messages.get(language, error_messages['uz'])

async def process_news_entry(entry):
    """Process a single news entry from RSS feed."""
    title = entry.get('title', '')
    link = entry.get('link', '')
    published = entry.get('published', datetime.now().isoformat())
    summary = entry.get('summary', '')
    source = entry.get('source', 'Unknown')
    
    # Check if the news already exists in the database
    if await database.is_news_exists(link):
        return None
    
    # Analyze news importance
    importance_score = await analyze_news_importance(title, summary)
    
    # Save to database (without key_points)
    await database.save_news(title, link, published, summary, source, importance_score, None)
    
    # Get current importance threshold
    threshold = await database.get_importance_threshold()
    
    # Return the entry if it's important enough
    if importance_score >= threshold:  # Dynamic threshold from database
        return {
            'title': title,
            'link': link,
            'published': published,
            'summary': summary,
            'source': source,
            'importance_score': importance_score
        }
    return None

async def fetch_and_process_news(limit=5):
    """
    Fetch and process all news entries.
    
    Args:
        limit (int): Maximum number of new entries to process
    """
    entries = await fetch_rss_feeds(limit)
    important_news = []
    
    for entry in entries:
        result = await process_news_entry(entry)
        if result:
            important_news.append(result)
    
    return important_news 