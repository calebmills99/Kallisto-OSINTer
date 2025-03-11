#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='kallisto_osinter',
    version='0.2.0',
    author='Vladislav Averett',
    author_email='avrtt@tuta.io',
    description='LLM-based OSINT tool for deep web search and data synthesis with advanced features',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests*', 'docs', 'examples']),
    install_requires=[
        'requests==2.32.3',
        'openai>=0.27.0',
        'beautifulsoup4==4.13.3',
        'lxml>=4.6.3',
        'colorama==0.4.6',
        'google-search-results==2.4.2',
        'httpx==0.28.1',
        'tenacity==9.0.0',
        'requests_html==0.10.0',
        'aiohttp==3.11.12',
        'urllib3==2.3.0',
        'asyncio==3.4.3',
        'lxml_html_clean',
        'html_clean',
        'anyio>=4.4.0',
        'zipp>=3.19.1',
        'validators==0.34.0',
        'tqdm==4.67.1',
        'ipwhois==1.3.0',
        'fake_useragent',
        'PyQt6==6.8.1',
        'dnspython>=2.6.1',
        'aiohttp-socks==0.10.1',
        'python-socks[asyncio]>=2.4.3',
        'langchain',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'kallisto=kallisto_osinter.src.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)