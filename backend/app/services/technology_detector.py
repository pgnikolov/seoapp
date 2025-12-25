from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re


class TechnologyDetector:
    """Открива технологии чрез fingerprinting на HTML, headers и URL patterns."""
    
    def detect(self, html: str, headers: Dict, url: str) -> dict:
        soup = BeautifulSoup(html, 'lxml')
        
        result = {
            'cms': None,
            'cms_version': None,
            'plugins': [],
            'javascript_libraries': [],
            'cache_systems': [],
            'cdn': None,
            'http_version': None,
            'tls_version': None,
            'tag_managers': [],
            'social_embeds': []
        }
        
        # CMS Detection
        cms_info = self._detect_cms(soup, html, headers)
        if cms_info:
            result['cms'] = cms_info.get('name')
            result['cms_version'] = cms_info.get('version')
        
        # Plugins
        result['plugins'] = self._detect_plugins(soup, html)
        
        # JavaScript libraries
        result['javascript_libraries'] = self._detect_js_libraries(soup, html)
        
        # Cache systems
        result['cache_systems'] = self._detect_cache(soup, headers)
        
        # CDN
        result['cdn'] = self._detect_cdn(headers, url)
        
        # HTTP/2 и TLS от headers
        result['http_version'] = headers.get('X-Protocol', '')
        result['tls_version'] = headers.get('X-TLS-Version', '')
        
        # Tag managers
        result['tag_managers'] = self._detect_tag_managers(soup, html)
        
        # Social embeds
        result['social_embeds'] = self._detect_social_embeds(soup, html)
        
        return result
    
    def _detect_cms(self, soup: BeautifulSoup, html: str, headers: Dict) -> Optional[Dict]:
        """Открива CMS и версия."""
        
        # WordPress
        if 'wp-content' in html or 'wp-includes' in html or 'wordpress' in html.lower():
            version = None
            # Версия от meta generator
            generator = soup.find('meta', {'name': 'generator'})
            if generator and generator.get('content'):
                content = generator.get('content', '').lower()
                if 'wordpress' in content:
                    version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', content)
                    if version_match:
                        version = version_match.group(1)
            return {'name': 'WordPress', 'version': version}
        
        # Drupal
        if 'drupal' in html.lower() or soup.find('meta', {'name': 'generator', 'content': re.compile('drupal', re.I)}):
            return {'name': 'Drupal', 'version': None}
        
        # Joomla
        if 'joomla' in html.lower() or soup.find('meta', {'name': 'generator', 'content': re.compile('joomla', re.I)}):
            return {'name': 'Joomla', 'version': None}
        
        # Shopify
        if 'shopify' in html.lower() or 'cdn.shopify.com' in html:
            return {'name': 'Shopify', 'version': None}
        
        # Magento
        if 'magento' in html.lower() or 'mage/' in html:
            return {'name': 'Magento', 'version': None}
        
        return None
    
    def _detect_plugins(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Открива plugins."""
        plugins = []
        
        # WordPress plugins
        if 'wp-content/plugins' in html:
            plugin_matches = re.findall(r'wp-content/plugins/([^/]+)', html)
            plugins.extend([p for p in plugin_matches if p not in plugins])
        
        # WooCommerce
        if 'woocommerce' in html.lower() or 'wc-' in html:
            plugins.append('WooCommerce')
        
        # Elementor
        if 'elementor' in html.lower() or 'elementor/' in html:
            plugins.append('Elementor')
        
        # Yoast SEO
        if 'yoast' in html.lower() or 'yoast-seo' in html:
            plugins.append('Yoast SEO')
        
        # Rank Math
        if 'rank-math' in html.lower():
            plugins.append('Rank Math')
        
        return list(set(plugins))
    
    def _detect_js_libraries(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Открива JavaScript библиотеки."""
        libraries = []
        
        # jQuery
        if 'jquery' in html.lower() or soup.find('script', src=re.compile(r'jquery', re.I)):
            libraries.append('jQuery')
        
        # Swiper
        if 'swiper' in html.lower() or 'swiper.js' in html.lower():
            libraries.append('Swiper')
        
        # React
        if 'react' in html.lower() or 'react-dom' in html.lower():
            libraries.append('React')
        
        # Vue
        if 'vue.js' in html.lower() or 'vue.min.js' in html.lower():
            libraries.append('Vue.js')
        
        # Angular
        if 'angular' in html.lower() or 'ng-' in html:
            libraries.append('Angular')
        
        return libraries
    
    def _detect_cache(self, soup: BeautifulSoup, headers: Dict) -> List[str]:
        """Открива cache системи."""
        cache_systems = []
        
        # От headers
        if 'X-Cache' in headers:
            cache_systems.append(headers['X-Cache'])
        if 'X-Cache-Status' in headers:
            cache_systems.append(headers['X-Cache-Status'])
        if 'CF-Cache-Status' in headers:
            cache_systems.append('Cloudflare Cache')
        if 'X-WP-Super-Cache' in headers:
            cache_systems.append('WP Super Cache')
        if 'X-W3TC-Minify' in headers:
            cache_systems.append('W3 Total Cache')
        
        return cache_systems
    
    def _detect_cdn(self, headers: Dict, url: str) -> Optional[str]:
        """Открива CDN."""
        # Cloudflare
        if 'cf-ray' in headers or 'cloudflare' in headers.get('Server', '').lower():
            return 'Cloudflare'
        
        # CloudFront
        if 'x-amz-cf-id' in headers:
            return 'Amazon CloudFront'
        
        # Fastly
        if 'fastly' in headers.get('Server', '').lower():
            return 'Fastly'
        
        # MaxCDN / StackPath
        if 'x-served-by' in headers:
            return 'StackPath'
        
        return None
    
    def _detect_tag_managers(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Открива tag managers."""
        tag_managers = []
        
        # Google Tag Manager
        if 'googletagmanager.com' in html or 'GTM-' in html:
            tag_managers.append('Google Tag Manager')
        
        # Adobe DTM
        if 'adobe.com/dtm' in html or 'satelliteLib' in html:
            tag_managers.append('Adobe DTM')
        
        return tag_managers
    
    def _detect_social_embeds(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Открива social embeds."""
        embeds = []
        
        # Facebook
        if 'facebook.com/plugins' in html or 'fb-root' in html:
            embeds.append('Facebook')
        
        # Twitter
        if 'twitter.com/widgets' in html or 'platform.twitter.com' in html:
            embeds.append('Twitter')
        
        # Instagram
        if 'instagram.com/embed' in html:
            embeds.append('Instagram')
        
        # YouTube
        if 'youtube.com/embed' in html or 'youtu.be' in html:
            embeds.append('YouTube')
        
        return embeds

