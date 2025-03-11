"""
Configuration module for Kallisto-OSINTer. Loads configuration settings from environment variables and provides default parameters.
"""

import os
import json

def load_config():
    """
    Loads configuration from environment variables and config files.
    Returns a dictionary with configuration settings.
    """
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'SERPER_API_KEY': os.getenv('SERPER_API_KEY', ''),
        'SCRAPINGBEE_API_KEY': os.getenv('SCRAPINGBEE_API_KEY', ''),
        'CACHE_DIR': os.getenv('CACHE_DIR', './cache'),
        'DEFAULT_USER_AGENT': os.getenv('DEFAULT_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
        'PROXY_LIST': os.getenv('PROXY_LIST', '[]')
    }
    try:
        config['PROXY_LIST'] = json.loads(config['PROXY_LIST'])
    except Exception:
        config['PROXY_LIST'] = []
    return config