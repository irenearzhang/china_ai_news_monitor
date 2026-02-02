"""
China AI News Monitor - News Fetcher Module

This module handles fetching and categorizing news articles from Chinese sources
using the MCP batch_web_search and extract_content_from_websites tools.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml
from dateutil import parser as date_parser
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Represents a news article."""
    title: str
    url: str
    source: str
    publish_date: datetime
    category: str
    summary: str = ""
    full_content: str = ""
    trust_score: float = 0.0
    keywords_matched: List[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['publish_date'] = self.publish_date.isoformat()
        return data


class NewsFetcher:
    """Fetches and processes news articles from Chinese sources."""
    
    def __init__(self, config_path: str = None):
        """Initialize the news fetcher with configuration."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config = self._load_config(config_path)
        self.categories = self.config.get('categories', {})
        self.source_weights = self.config.get('source_weights', {})
        self.filtering = self.config.get('filtering', {})
        
        # Timezone setup
        self.timezone = pytz.timezone(
            self.config.get('monitoring', {}).get('timezone', 'Asia/Shanghai')
        )
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def get_search_queries(self) -> Dict[str, List[str]]:
        """Generate search queries for each category."""
        queries = {}
        for category, config in self.categories.items():
            keywords = config.get('keywords', [])
            # Create search queries with date filter
            queries[category] = [f"{keyword} 2026" for keyword in keywords[:5]]
        return queries
    
    def filter_article_by_source(self, source: str) -> float:
        """Get trust score for an article based on its source."""
        # Normalize source name for matching
        source_lower = source.lower()
        
        # Direct match
        for known_source, score in self.source_weights.items():
            if known_source in source_lower or source_lower in known_source:
                return score
        
        # Default trust score for unknown sources
        return 0.5
    
    def parse_chinese_date(self, date_str: str) -> Optional[datetime]:
        """Parse Chinese date formats."""
        if not date_str:
            return None
        
        # Common Chinese date formats
        formats = [
            "%Y年%m月%d日",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m月%d日",
            "刚刚",
            "几分钟前",
            "%H:%M",
        ]
        
        # Handle relative time
        if "分钟" in date_str:
            minutes = int(''.join(filter(str.isdigit, date_str)) or 0)
            return datetime.now(self.timezone) - timedelta(minutes=minutes)
        if "小时" in date_str:
            hours = int(''.join(filter(str.isdigit, date_str)) or 0)
            return datetime.now(self.timezone) - timedelta(hours=hours)
        if "昨天" in date_str:
            return datetime.now(self.timezone) - timedelta(days=1)
        
        # Try parsing as standard datetime
        try:
            return date_parser.parse(date_str)
        except:
            return None
    
    def is_article_recent(self, publish_date: datetime) -> bool:
        """Check if article is within the maximum age threshold."""
        if not publish_date:
            # If no date found, assume it's not recent (to avoid old articles)
            return False
        
        max_age = self.filtering.get('max_age_days', 1)
        now = datetime.now(self.timezone)
        
        if publish_date.tzinfo is None:
            publish_date = self.timezone.localize(publish_date)
        
        age = now - publish_date
        return age.total_seconds() <= max_age * 24 * 3600
    
    def is_article_too_old(self, publish_date: datetime, max_days: int = 90) -> bool:
        """Check if article is too old (e.g., older than 90 days)."""
        if not publish_date:
            return True  # No date = treat as too old
        
        now = datetime.now(self.timezone)
        if publish_date.tzinfo is None:
            publish_date = self.timezone.localize(publish_date)
        
        age = now - publish_date
        return age.total_seconds() > max_days * 24 * 3600
    
    def get_max_article_age_hours(self) -> int:
        """
        Get the maximum article age in hours based on the current day.
        - Monday: 72 hours (covers weekend)
        - Tuesday-Friday: 24 hours
        - Saturday-Sunday: 24 hours (but won't run on weekends)
        """
        # Get current day of week (Monday=0, Sunday=6 in Python's weekday())
        today = datetime.now(self.timezone)
        day_of_week = today.weekday()
        
        # Monday is day 0 in Python, so check if it's Monday
        if day_of_week == 0:  # Monday
            return self.config.get('monitoring', {}).get('monday_hours', 72)
        else:
            return self.config.get('monitoring', {}).get('normal_hours', 24)
    
    def is_article_within_time_window(self, publish_date: datetime) -> bool:
        """Check if article is within the appropriate time window (24h or 72h for Monday)."""
        if not publish_date:
            return False
        
        max_hours = self.get_max_article_age_hours()
        now = datetime.now(self.timezone)
        
        if publish_date.tzinfo is None:
            publish_date = self.timezone.localize(publish_date)
        
        age = now - publish_date
        return age.total_seconds() <= max_hours * 3600
    
    def extract_keywords_matched(self, title: str, keywords: List[str]) -> List[str]:
        """Extract which keywords matched in the title."""
        matched = []
        title_lower = title.lower()
        for keyword in keywords:
            if keyword.lower() in title_lower:
                matched.append(keyword)
        return matched
    
    def process_search_results(self, category: str, search_data: Dict, keywords: List[str]) -> List[Article]:
        """Process search results and create Article objects."""
        articles = []
        seen_urls = set()  # For deduplication
        category_config = self.categories.get(category, {})
        sources = category_config.get('sources', [])
        
        for result in search_data.get('results', []):
            try:
                title = result.get('title', '')
                url = result.get('url', '')
                source = result.get('source', '')
                date_str = result.get('date', '')
                
                # Skip if URL already seen (duplicate detection)
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                # Parse date
                publish_date = self.parse_chinese_date(date_str)
                
                # Check if article is within the appropriate time window
                # Monday: last 72 hours, Tuesday-Friday: last 24 hours
                if not self.is_article_within_time_window(publish_date):
                    continue
                
                # Skip articles that are too old (e.g., older than 90 days)
                if publish_date and self.is_article_too_old(publish_date):
                    continue
                
                # Calculate trust score
                trust_score = self.filter_article_by_source(source)
                min_score = self.filtering.get('min_trust_score', 0.7)
                if trust_score < min_score:
                    continue
                
                # Extract matched keywords
                matched_keywords = self.extract_keywords_matched(title, keywords)
                
                article = Article(
                    title=title,
                    url=url,
                    source=source,
                    publish_date=publish_date or datetime.now(self.timezone),
                    category=category_config.get('name', category),
                    trust_score=trust_score,
                    keywords_matched=matched_keywords
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error processing search result: {e}")
                continue
        
        # Sort by trust score and date
        articles.sort(key=lambda x: (-x.trust_score, x.publish_date), reverse=True)
        
        # Limit number of articles
        max_articles = self.config.get('monitoring', {}).get('max_articles_per_category', 10)
        return articles[:max_articles]
    
    def extract_article_content(self, articles: List[Article]) -> List[Article]:
        """
        Extract full content from articles.
        
        Note: This method prepares articles for content extraction.
        The actual extraction should be done using the MCP extract_content_from_websites tool.
        """
        logger.info(f"Prepared {len(articles)} articles for content extraction")
        return articles
    
    def fetch_category_news(self, category: str, web_search_func) -> List[Article]:
        """
        Fetch news for a specific category.
        
        Args:
            category: The category name (e.g., 'ai_releases', 'government_policies')
            web_search_func: Function to perform web search (should be MCP batch_web_search)
        
        Returns:
            List of Article objects
        """
        if category not in self.categories:
            logger.error(f"Unknown category: {category}")
            return []
        
        category_config = self.categories[category]
        keywords = category_config.get('keywords', [])
        
        logger.info(f"Fetching news for category: {category}")
        logger.info(f"Keywords: {keywords[:3]}...")
        
        # This method should be implemented to call the MCP web search tool
        # The actual implementation will depend on how the tool is integrated
        return []
    
    def run_daily_fetch(self, web_search_func, extract_func) -> Dict[str, List[Article]]:
        """
        Run the daily news fetch for all categories.
        
        Args:
            web_search_func: MCP batch_web_search function
            extract_func: MCP extract_content_from_websites function
        
        Returns:
            Dictionary mapping category names to lists of Article objects
        """
        results = {}
        queries = self.get_search_queries()
        
        for category, search_queries in queries.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing category: {category}")
            logger.info(f"{'='*60}")
            
            try:
                # Perform web searches for this category
                search_results = web_search_func(
                    queries=[{"query": q} for q in search_queries],
                    display_text=f"Searching {category} news"
                )
                
                # Process results
                keywords = self.categories.get(category, {}).get('keywords', [])
                articles = self.process_search_results(category, search_results, keywords)
                
                # Extract full content if we have articles
                if articles:
                    articles = self.extract_article_content(articles)
                
                results[category] = articles
                logger.info(f"Found {len(articles)} articles in {category}")
                
            except Exception as e:
                logger.error(f"Error fetching {category}: {e}")
                results[category] = []
        
        return results


def load_articles_from_file(filepath: str) -> Dict[str, List[Article]]:
    """Load previously fetched articles from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles_dict = {}
        for category, articles_data in data.items():
            articles = []
            for art_data in articles_data:
                art_data['publish_date'] = date_parser.parse(art_data['publish_date'])
                articles.append(Article(**art_data))
            articles_dict[category] = articles
        
        return articles_dict
    except Exception as e:
        logger.error(f"Error loading articles from {filepath}: {e}")
        return {}


def save_articles_to_file(articles_dict: Dict[str, List[Article]], filepath: str):
    """Save fetched articles to JSON file."""
    try:
        data = {}
        for category, articles in articles_dict.items():
            data[category] = [article.to_dict() for article in articles]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved articles to {filepath}")
    except Exception as e:
        logger.error(f"Error saving articles to {filepath}: {e}")


if __name__ == "__main__":
    # Test the news fetcher
    fetcher = NewsFetcher()
    print("News Fetcher initialized successfully")
    print(f"Categories: {list(fetcher.categories.keys())}")
