import whois
import socket
from urllib.parse import urlparse
from typing import Dict, Optional
from datetime import datetime


class WhoisEnricher:
    """Обогатява данните с WHOIS информация за домейна и IP."""
    
    def enrich(self, domain: str, ip_address: Optional[str] = None) -> dict:
        """
        Взима WHOIS данни за домейна и IP адреса.
        """
        result = {
            'domain_whois': self._get_domain_whois(domain),
            'ip_whois': None,
            'same_ip_websites': []
        }
        
        if ip_address:
            result['ip_whois'] = self._get_ip_whois(ip_address)
            # За други сайтове на същия IP - не го правим засега (нямаме достъп до такава база)
            result['same_ip_websites'] = []
        
        return result
    
    def _get_domain_whois(self, domain: str) -> dict:
        """Взима WHOIS данни за домейна."""
        try:
            # Премахва протокола ако има
            clean_domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
            
            w = whois.whois(clean_domain)
            
            # Парсване на дати
            creation_date = None
            expiry_date = None
            
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                if isinstance(creation_date, datetime):
                    creation_date = creation_date.isoformat()
            
            if w.expiration_date:
                if isinstance(w.expiration_date, list):
                    expiry_date = w.expiration_date[0]
                else:
                    expiry_date = w.expiration_date
                if isinstance(expiry_date, datetime):
                    expiry_date = expiry_date.isoformat()
            
            # Name servers
            name_servers = []
            if w.name_servers:
                if isinstance(w.name_servers, list):
                    name_servers = [str(ns).lower() for ns in w.name_servers]
                else:
                    name_servers = [str(w.name_servers).lower()]
            
            return {
                'registrar': str(w.registrar) if w.registrar else None,
                'creation_date': creation_date,
                'expiry_date': expiry_date,
                'name_servers': name_servers,
                'status': w.status if w.status else None,
                'domain_age_days': self._calculate_domain_age(creation_date) if creation_date else None
            }
        except Exception as e:
            return {
                'registrar': None,
                'creation_date': None,
                'expiry_date': None,
                'name_servers': [],
                'status': None,
                'domain_age_days': None,
                'error': str(e)
            }
    
    def _get_ip_whois(self, ip_address: str) -> dict:
        """Взима WHOIS данни за IP адреса (базови данни)."""
        try:
            # Използваме socket за reverse DNS
            hostname = None
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
            except:
                pass
            
            # За пълни WHOIS данни за IP трябва специализирана библиотека,
            # но за MVP ще върнем основни данни
            return {
                'ip': ip_address,
                'hostname': hostname,
                'organization': None,  # Изисква IP WHOIS API
                'country': None  # Изисква GeoIP база
            }
        except Exception as e:
            return {
                'ip': ip_address,
                'error': str(e)
            }
    
    def _calculate_domain_age(self, creation_date_str: str) -> Optional[int]:
        """Изчислява възрастта на домейна в дни."""
        try:
            if isinstance(creation_date_str, str):
                # Парсване на ISO формат
                if 'T' in creation_date_str:
                    creation_date = datetime.fromisoformat(creation_date_str.replace('Z', '+00:00'))
                else:
                    creation_date = datetime.fromisoformat(creation_date_str)
            else:
                creation_date = creation_date_str
            
            now = datetime.now()
            if creation_date.tzinfo:
                # Ако има timezone, нормализираме
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            
            delta = now - creation_date
            return delta.days
        except:
            return None

