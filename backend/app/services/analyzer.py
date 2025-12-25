from urllib.parse import urlparse
from typing import Dict, Any
from app.services.crawler import WebsiteCrawler
from app.services.technology_detector import TechnologyDetector
from app.services.seo_parser import SEOParser
from app.services.metadata_parser import MetadataParser
from app.services.whois_enricher import WhoisEnricher
from app.services.infrastructure_detector import InfrastructureDetector


class WebsiteAnalyzer:
    """Главният анализатор, който координира всички модули."""
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        Анализира URL и връща пълен snapshot.
        """
        crawler = WebsiteCrawler()
        
        try:
            # 1. Взимане на HTML и инфраструктурни данни
            crawl_data = await crawler.fetch(url)
            html = crawl_data['html']
            headers = crawl_data['headers']
            domain = crawl_data['domain']
            ip_address = crawl_data.get('ip_address')
            
            # 2. Technology Detection
            tech_detector = TechnologyDetector()
            technology_data = tech_detector.detect(html, headers, url)
            
            # 3. On-page SEO
            seo_parser = SEOParser()
            seo_data = seo_parser.parse(html, crawl_data['final_url'])
            
            # 4. Metadata & Structured Data
            metadata_parser = MetadataParser()
            metadata_data = metadata_parser.parse(html)
            
            # 5. WHOIS & IP WHOIS
            whois_enricher = WhoisEnricher()
            whois_data = whois_enricher.enrich(domain, ip_address)
            
            # 6. Infrastructure Detection
            infra_detector = InfrastructureDetector()
            infra_data = infra_detector.detect(domain, ip_address, headers)
            
            # Събиране на всички данни
            result = {
                'url': url,
                'final_url': crawl_data['final_url'],
                'domain_and_infrastructure': {
                    'domain': domain,
                    'domain_age_days': whois_data['domain_whois'].get('domain_age_days'),
                    'registrar': whois_data['domain_whois'].get('registrar'),
                    'expiry_date': whois_data['domain_whois'].get('expiry_date'),
                    'name_servers': whois_data['domain_whois'].get('name_servers', []),
                    'ip_address': ip_address,
                    'hosting_provider': infra_data.get('hosting_provider'),
                    'server_location_country': infra_data.get('server_location_country'),
                    'web_server': crawl_data.get('web_server'),
                    'http_to_https_redirect': crawl_data.get('http_to_https_redirect', False),
                    'response_headers': headers
                },
                'technology_detection': technology_data,
                'on_page_seo': seo_data,
                'metadata_and_structured_data': metadata_data,
                'whois_and_ip_whois': {
                    'domain_whois': whois_data['domain_whois'],
                    'ip_whois': whois_data['ip_whois'],
                    'same_ip_websites': whois_data['same_ip_websites']
                }
            }
            
            return result
            
        finally:
            await crawler.close()

