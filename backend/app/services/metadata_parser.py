from bs4 import BeautifulSoup
from typing import Dict, List
import json
import re


class MetadataParser:
    """Парсва metadata и structured data."""
    
    def parse(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'lxml')
        
        result = {
            'canonical': self._get_canonical(soup),
            'open_graph': self._get_open_graph(soup),
            'twitter_cards': self._get_twitter_cards(soup),
            'json_ld': self._get_json_ld(soup),
            'feeds': self._get_feeds(soup),
            'robots_meta': self._get_robots_meta(soup)
        }
        
        return result
    
    def _get_canonical(self, soup: BeautifulSoup) -> str:
        """Взима canonical URL."""
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical:
            return canonical.get('href', '')
        return ''
    
    def _get_open_graph(self, soup: BeautifulSoup) -> dict:
        """Взима OpenGraph tags."""
        og_tags = {}
        og_meta = soup.find_all('meta', {'property': re.compile(r'^og:', re.I)})
        
        for meta in og_meta:
            prop = meta.get('property', '').lower()
            content = meta.get('content', '')
            # Премахва 'og:' префикса
            key = prop.replace('og:', '')
            og_tags[key] = content
        
        return og_tags
    
    def _get_twitter_cards(self, soup: BeautifulSoup) -> dict:
        """Взима Twitter Card tags."""
        twitter_tags = {}
        twitter_meta = soup.find_all('meta', {'name': re.compile(r'^twitter:', re.I)})
        
        for meta in twitter_meta:
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            # Премахва 'twitter:' префикса
            key = name.replace('twitter:', '')
            twitter_tags[key] = content
        
        return twitter_tags
    
    def _get_json_ld(self, soup: BeautifulSoup) -> List[dict]:
        """Взима JSON-LD structured data."""
        json_ld_data = []
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in scripts:
            try:
                content = script.string
                if content:
                    data = json.loads(content)
                    json_ld_data.append(data)
            except:
                pass
        
        return json_ld_data
    
    def _get_feeds(self, soup: BeautifulSoup) -> List[str]:
        """Взима RSS/JSON feeds."""
        feeds = []
        
        # RSS
        rss_links = soup.find_all('link', {'type': re.compile(r'application/(rss|atom)', re.I)})
        for link in rss_links:
            href = link.get('href', '')
            if href:
                feeds.append(href)
        
        # JSON Feed
        json_feeds = soup.find_all('link', {'type': 'application/json'})
        for link in json_feeds:
            href = link.get('href', '')
            if 'feed' in href.lower() or 'json' in href.lower():
                feeds.append(href)
        
        return feeds
    
    def _get_robots_meta(self, soup: BeautifulSoup) -> str:
        """Взима robots meta tag."""
        robots = soup.find('meta', {'name': 'robots'})
        if robots:
            return robots.get('content', '')
        return ''

