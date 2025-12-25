import socket
from urllib.parse import urlparse
from typing import Dict, Optional
import re


class InfrastructureDetector:
    """Открива инфраструктурни данни - hosting provider, server location и т.н."""
    
    def detect(self, domain: str, ip_address: Optional[str], headers: Dict) -> dict:
        """
        Открива hosting provider и server location от IP и headers.
        """
        result = {
            'hosting_provider': None,
            'server_location_country': None
        }
        
        if ip_address:
            # Опитваме се да открием hosting provider от hostname
            hostname = self._get_hostname(ip_address)
            if hostname:
                result['hosting_provider'] = self._detect_hosting_from_hostname(hostname)
        
        # Server location - за MVP не можем да го определим без GeoIP база
        # Оставяме празно
        
        return result
    
    def _get_hostname(self, ip_address: str) -> Optional[str]:
        """Взима hostname от IP."""
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except:
            return None
    
    def _detect_hosting_from_hostname(self, hostname: str) -> Optional[str]:
        """Открива hosting provider от hostname."""
        hostname_lower = hostname.lower()
        
        # Познати hosting providers
        providers = {
            'amazonaws.com': 'Amazon AWS',
            'cloudflare.com': 'Cloudflare',
            'googleusercontent.com': 'Google Cloud',
            'azure': 'Microsoft Azure',
            'digitalocean': 'DigitalOcean',
            'linode': 'Linode',
            'ovh': 'OVH',
            'hetzner': 'Hetzner',
            'bluehost': 'Bluehost',
            'godaddy': 'GoDaddy',
            'hostgator': 'HostGator',
            'siteground': 'SiteGround',
            'wpengine': 'WP Engine',
            'kinsta': 'Kinsta'
        }
        
        for key, provider in providers.items():
            if key in hostname_lower:
                return provider
        
        return None

