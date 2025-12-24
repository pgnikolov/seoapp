import re
from urllib.parse import urlparse, urljoin, urlunparse

def normalize_url(url: str, base_url: str = None) -> str:
    """
    Нормализира URL адреса – маха фрагменти, добавя базов URL ако е релативен.
    """
    if not url:
        return ""
    
    if base_url:
        url = urljoin(base_url, url)
    
    parsed = urlparse(url)
    # Махаме фрагменти (#) и нормализираме пътя
    normalized_path = parsed.path.rstrip('/')
    if not normalized_path:
        normalized_path = '/'
    
    # Реконструираме URL без фрагмент и query параметри (често са тракинг)
    # За SEO цели обикновено искаме чист URL, но понякога query-тата са важни.
    # Тук ще ги запазим за всеки случай, но ще махнем фрагмента.
    
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        normalized_path,
        parsed.params,
        parsed.query,
        ""
    ))

def is_same_domain(url1: str, url2: str, include_subdomains: bool = False) -> bool:
    """
    Проверява дали два URL-а са от един и същи домейн.
    """
    p1 = urlparse(url1).netloc.lower()
    p2 = urlparse(url2).netloc.lower()
    
    if include_subdomains:
        # Тук може да се ползва tldextract за по-точно, но за простота:
        d1 = '.'.join(p1.split('.')[-2:])
        d2 = '.'.join(p2.split('.')[-2:])
        return d1 == d2
    
    return p1 == p2

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
