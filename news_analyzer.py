import feedparser
import asyncio
import openai
from openai import OpenAI
import os
from datetime import datetime
import database

# RSS feed sources
RSS_SOURCES = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss",
    "CoinTelegraph": "https://cointelegraph.com/rss"
}

IMPORTANCE_THRESHOLD = 0.3

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
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a cryptocurrency market analyst who evaluates news impact on crypto prices."},
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

async def extract_key_points(title, summary):
    """
    Extract key points from news using OpenAI to highlight important aspects.
    Returns a concise summary of the most important points.
    """
    prompt = f"""
    Analyze the following cryptocurrency news and extract the 2-3 most important facts or implications for crypto markets.
    Focus on regulatory changes, adoption news, market impacts, or security issues.
    
    Title: {title}
    Summary: {summary}
    
    Return only the key points in bullet format in Uzbek language:
    """
    
    try:
        # Create client with new API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a cryptocurrency analyst who extracts key insights from news."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        # Get key points from new API structure
        key_points = response.choices[0].message.content.strip()
        return key_points
    except Exception as e:
        print(f"Error extracting key points: {e}")
        return "• Xabar tahlil qilinmadi"

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
    
    # Extract key points for important news
    key_points = None
    if importance_score >= IMPORTANCE_THRESHOLD:  # Only for important news
        key_points = await extract_key_points(title, summary)
    
    # Save to database
    await database.save_news(title, link, published, summary, source, importance_score, key_points)
    
    # Return the entry if it's important enough
    if importance_score >= IMPORTANCE_THRESHOLD:  # Threshold for important news
        return {
            'title': title,
            'link': link,
            'published': published,
            'summary': summary,
            'source': source,
            'importance_score': importance_score,
            'key_points': key_points
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