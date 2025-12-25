import httpx
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple
import socket


class WebsiteCrawler:
    """Взима HTML съдържанието и инфраструктурни данни от URL."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def fetch(self, url: str) -> Dict:
        """
        Взима страницата и връща HTML, headers, redirect chain и инфраструктурни данни.
        """
        try:
            response = await self.client.get(url)
            html = response.text
            headers = dict(response.headers)
            
            # Парсване на URL за домейн
            parsed = urlparse(str(response.url))
            domain = parsed.netloc
            
            # IP адрес
            ip_address = None
            try:
                ip_address = socket.gethostbyname(domain)
            except:
                pass
            
            # Redirect chain
            redirect_chain = []
            if response.history:
                redirect_chain = [str(r.url) for r in response.history]
            redirect_chain.append(str(response.url))
            
            # Проверка за HTTP -> HTTPS redirect
            http_to_https = False
            if redirect_chain:
                first_url = redirect_chain[0]
                final_url = redirect_chain[-1]
                if first_url.startswith('http://') and final_url.startswith('https://'):
                    http_to_https = True
            
            # Web server от headers
            web_server = headers.get('Server', '')
            
            # HTTP/2 и TLS
            http_version = 'HTTP/1.1'
            if hasattr(response, 'http_version'):
                http_version = f"HTTP/{response.http_version}"
            
            return {
                'html': html,
                'headers': headers,
                'status_code': response.status_code,
                'final_url': str(response.url),
                'domain': domain,
                'ip_address': ip_address,
                'redirect_chain': redirect_chain,
                'http_to_https_redirect': http_to_https,
                'web_server': web_server,
                'http_version': http_version,
                'content_length': len(response.content)
            }
        except Exception as e:
            raise Exception(f"Грешка при взимане на страницата: {str(e)}")
    
    async def close(self):
        await self.client.aclose()

