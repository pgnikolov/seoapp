import httpx
from bs4 import BeautifulSoup
from protego import Protego
from ..utils.url import normalize_url, is_same_domain, is_valid_url
import asyncio
import logging
from typing import List, Set, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, start_url: str, max_pages: int = 30, max_depth: int = 2, 
                 mode: str = "domain", include_subdomains: bool = False):
        self.start_url = normalize_url(start_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.mode = mode
        self.include_subdomains = include_subdomains
        
        self.visited_urls: Set[str] = set()
        self.queue = asyncio.Queue()
        self.results: List[Dict[str, Any]] = []
        self.robots_cache: Dict[str, Protego] = {}
        
        self.base_netloc = urlparse(self.start_url).netloc
        self.headers = {
            "User-Agent": "SEOAppCrawler/1.0 (+http://localhost:3000)"
        }

    async def get_robots(self, client: httpx.AsyncClient, url: str) -> Protego:
        parsed = urlparse(url)
        root_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        if root_url in self.robots_cache:
            return self.robots_cache[root_url]
        
        try:
            resp = await client.get(root_url, timeout=5.0)
            if resp.status_code == 200:
                rp = Protego.parse(resp.text)
            else:
                rp = Protego.parse("")
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt for {root_url}: {e}")
            rp = Protego.parse("")
        
        self.robots_cache[root_url] = rp
        return rp

    async def can_fetch(self, client: httpx.AsyncClient, url: str) -> bool:
        rp = await self.get_robots(client, url)
        return rp.can_fetch(url, self.headers["User-Agent"])

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Извличаме мета данни, заглавия и текст от HTML-а.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        canonical_url = normalize_url(canonical['href'], url) if canonical and canonical.get('href') else url
        
        # Meta tags
        meta_desc = ""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            meta_desc = desc_tag.get('content', '')
            
        # Title
        title = ""
        if soup.title:
            title = soup.title.string or ""
        
        # Headings
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]
        
        # Body text - почистване от скриптове и навигация
        for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script_or_style.decompose()
            
        body_text = soup.get_text(separator=' ', strip=True)
        
        # Internal links and anchor text
        internal_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = normalize_url(href, url)
            anchor_text = a.get_text(strip=True)
            
            if is_valid_url(full_url) and is_same_domain(self.start_url, full_url, self.include_subdomains):
                internal_links.append({
                    "url": full_url,
                    "anchor": anchor_text
                })

        return {
            "url": url,
            "canonical": canonical_url,
            "title": title,
            "meta_description": meta_desc,
            "h1": h1s,
            "h2": h2s,
            "h3": h3s,
            "body": body_text,
            "links": internal_links
        }

    async def run(self):
        """
        Основен цикъл на crawler-а. Използваме BFS опашка.
        """
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            await self.queue.put((self.start_url, 0))
            
            while not self.queue.empty() and len(self.results) < self.max_pages:
                current_url, depth = await self.queue.get()
                
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                
                if not await self.can_fetch(client, current_url):
                    logger.info(f"Skipping {current_url} due to robots.txt")
                    continue

                try:
                    # Delay per request (respecting rate limit)
                    await asyncio.sleep(0.5) 
                    
                    resp = await client.get(current_url, timeout=10.0)
                    if resp.status_code != 200 or 'text/html' not in resp.headers.get('content-type', ''):
                        continue
                    
                    content = await self.extract_content(resp.text, str(resp.url))
                    self.results.append(content)
                    
                    # Ако сме в режим на целия домейн и не сме превишили дълбочината
                    if self.mode == "domain" and depth < self.max_depth:
                        for link_data in content["links"]:
                            link_url = link_data["url"]
                            if link_url not in self.visited_urls:
                                await self.queue.put((link_url, depth + 1))
                    
                except Exception as e:
                    logger.error(f"Error crawling {current_url}: {e}")
                
                finally:
                    self.queue.task_done()

        return self.results
