"""
DNS Lookup module.
Provides functions to perform DNS lookups using dnspython.
"""

import dns.resolver
from dns import exception as dns_exception
from src.utils.logger import get_logger

logger = get_logger(__name__)

def lookup_dns(domain, record_types=None):
    """
    Performs DNS lookup for a domain for specified record types.
    If record_types is None, defaults to ['A', 'MX', 'NS', 'TXT'].
    Returns a dictionary with record type as key and list of records as value.
    """
    if record_types is None:
        record_types = ['A', 'MX', 'NS', 'TXT']
    
    records = {}
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [r.to_text() for r in answers]
            logger.info("DNS %s records for %s: %s", rtype, domain, records[rtype])
        except dns_exception.DNSException as e:
            logger.error("DNS lookup for %s record on %s failed: %s", rtype, domain, str(e))
            records[rtype] = []
    return records