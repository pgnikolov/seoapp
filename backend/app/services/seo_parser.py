from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, List
import re


class SEOParser:
    """Парсва on-page SEO данни от HTML."""
    
    def parse(self, html: str, base_url: str) -> dict:
        soup = BeautifulSoup(html, 'lxml')
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        result = {
            'title': self._get_title(soup),
            'meta_description': self._get_meta_description(soup),
            'language': self._get_language(soup),
            'page_size': len(html.encode('utf-8')),
            'text_size': len(soup.get_text()),
            'text_to_code_ratio': self._calculate_text_ratio(html, soup),
            'headings': self._get_headings(soup),
            'links': self._analyze_links(soup, base_domain),
            'images': self._analyze_images(soup)
        }
        
        return result
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Взима title tag."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ''
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Взима meta description."""
        meta_desc = soup.find('meta', {'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', {'property': 'og:description'})
        return meta_desc.get('content', '') if meta_desc else ''
    
    def _get_language(self, soup: BeautifulSoup) -> str:
        """Взима език на страницата."""
        html_tag = soup.find('html')
        if html_tag:
            lang = html_tag.get('lang')
            if lang:
                return lang
        
        meta_lang = soup.find('meta', {'http-equiv': 'Content-Language'})
        if meta_lang:
            return meta_lang.get('content', '')
        
        return ''
    
    def _calculate_text_ratio(self, html: str, soup: BeautifulSoup) -> float:
        """Изчислява text-to-code ratio."""
        text_size = len(soup.get_text())
        total_size = len(html)
        if total_size == 0:
            return 0.0
        return round((text_size / total_size) * 100, 2)
    
    def _get_headings(self, soup: BeautifulSoup) -> dict:
        """Взима всички headings H1-H6."""
        headings = {
            'h1': {'count': 0, 'content': []},
            'h2': {'count': 0, 'content': []},
            'h3': {'count': 0, 'content': []},
            'h4': {'count': 0, 'content': []},
            'h5': {'count': 0, 'content': []},
            'h6': {'count': 0, 'content': []}
        }
        
        for level in range(1, 7):
            tag_name = f'h{level}'
            tags = soup.find_all(tag_name)
            headings[tag_name]['count'] = len(tags)
            headings[tag_name]['content'] = [tag.get_text(strip=True) for tag in tags]
        
        return headings
    
    def _analyze_links(self, soup: BeautifulSoup, base_domain: str) -> dict:
        """Анализира всички линкове."""
        links = soup.find_all('a', href=True)
        
        internal = []
        external = []
        nofollow = []
        duplicated = []
        
        seen_urls = {}
        
        for link in links:
            href = link.get('href', '')
            if not href:
                continue
            
            # Абсолютен URL
            absolute_url = urljoin(base_domain, href)
            parsed = urlparse(absolute_url)
            
            # Проверка за nofollow
            rel = link.get('rel', [])
            if isinstance(rel, list):
                rel_str = ' '.join(rel).lower()
            else:
                rel_str = str(rel).lower()
            
            if 'nofollow' in rel_str:
                nofollow.append(absolute_url)
            
            # Вътрешен или външен
            if parsed.netloc == urlparse(base_domain).netloc or not parsed.netloc:
                internal.append(absolute_url)
            else:
                external.append(absolute_url)
            
            # Дублирани
            if absolute_url in seen_urls:
                if absolute_url not in duplicated:
                    duplicated.append(absolute_url)
            else:
                seen_urls[absolute_url] = True
        
        return {
            'internal': len(internal),
            'external': len(external),
            'nofollow': len(nofollow),
            'duplicated': len(duplicated)
        }
    
    def _analyze_images(self, soup: BeautifulSoup) -> dict:
        """Анализира всички изображения."""
        images = soup.find_all('img')
        
        missing_alt = []
        duplicated = []
        with_title = []
        
        seen_srcs = {}
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            if not alt or alt.strip() == '':
                missing_alt.append(src)
            
            if title:
                with_title.append(src)
            
            if src:
                if src in seen_srcs:
                    if src not in duplicated:
                        duplicated.append(src)
                else:
                    seen_srcs[src] = True
        
        return {
            'missing_alt': len(missing_alt),
            'duplicated': len(duplicated),
            'with_title': len(with_title)
        }

