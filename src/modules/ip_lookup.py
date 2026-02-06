"""
IP Lookup module.
Provides functions to perform IP address lookup using ipwhois and DNS records using dnspython.
"""

from ipwhois import IPWhois
from dns import resolver, exception as dns_exception
from src.utils.logger import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed

logger = get_logger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def lookup_ip(ip_address):
    """
    Performs an IP lookup using ipwhois.
    Returns a dictionary of information about the IP address.
    """
    try:
        obj = IPWhois(ip_address)
        result = obj.lookup_rdap(depth=1)
        logger.info("IP lookup successful for %s", ip_address)
        return result
    except Exception as e:
        logger.error("IP lookup failed for %s: %s", ip_address, str(e))
        raise

def get_dns_records(domain, record_type="A"):
    """
    Retrieves DNS records for the given domain.
    Supported record types: A, MX, NS, TXT, etc.
    Returns a list of records.
    """
    try:
        answers = resolver.resolve(domain, record_type)
        records = [r.to_text() for r in answers]
        logger.info("DNS records retrieved for %s (%s): %s", domain, record_type, records)
        return records
    except dns_exception.DNSException as e:
        logger.error("DNS lookup failed for %s: %s", domain, str(e))
        return []

def comprehensive_ip_analysis(ip_address, domain=None):
    """
    Performs comprehensive analysis including IP lookup and DNS records if domain is provided.
    Returns a combined dictionary of results.
    """
    ip_info = lookup_ip(ip_address)
    dns_info = {}
    if domain:
        dns_info = {
            "A": get_dns_records(domain, "A"),
            "MX": get_dns_records(domain, "MX"),
            "NS": get_dns_records(domain, "NS"),
            "TXT": get_dns_records(domain, "TXT")
        }
    combined = {
        "ip_info": ip_info,
        "dns_info": dns_info
    }
    return combined