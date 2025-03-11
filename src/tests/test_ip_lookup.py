"""
Unit tests for IP Lookup module.
"""

import unittest
from src.modules.ip_lookup import lookup_ip, get_dns_records, comprehensive_ip_analysis

class TestIPLookup(unittest.TestCase):
    def test_lookup_ip(self):
        # Use a known public IP (example: 8.8.8.8)
        result = lookup_ip("8.8.8.8")
        self.assertIsInstance(result, dict)
    
    def test_get_dns_records(self):
        records = get_dns_records("example.com", "A")
        self.assertIsInstance(records, list)
    
    def test_comprehensive_ip_analysis(self):
        result = comprehensive_ip_analysis("8.8.8.8", domain="example.com")
        self.assertIn("ip_info", result)
        self.assertIn("dns_info", result)

if __name__ == "__main__":
    unittest.main()