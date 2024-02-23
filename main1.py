import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# URL Arrays for existing sitemap formats
urls_existing_format = [
    'https://www.kevinrchant.com/post-sitemap.xml',
    'https://data-mozart.com/post-sitemap.xml',
    'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'https://thomas-leblanc.com/sitemap-1.xml',
]

# URL Arrays for Brunner sitemap format
urls_brunner_format = [
    'https://en.brunner.bi/blog-posts-sitemap.xml',
]

def fetch_sitemap(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def parse_existing_format(url):
    content = fetch_sitemap(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'xml')
    urls = []
    for url in soup.find_all('url'):
        loc = url.find('loc').text
        lastmod = url.find('lastmod')
        lastmod = lastmod.text if lastmod else None
        urls.append({'URL': loc, 'Last Modified': lastmod})
    return urls

def parse_brunner_format(url):
    content = fetch_sitemap(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'xml')
    urls = []
    for url in soup.find_all('url'):
        loc = url.find('loc').text
        lastmod = url.find('lastmod').text if url.find('lastmod') else None
        # Convert lastmod to datetime object, if present
        if lastmod:
            lastmod = datetime.strptime(lastmod, '%Y-%m-%d').isoformat()
        urls.append({'URL': loc, 'Last Modified': lastmod})
    return urls

def process_urls(urls, parser_function):
    all_results = []
    for url in urls:
        result = parser_function(url)
        all_results.extend(result)
    return all_results

def display_results(results):
    df = pd.DataFrame(results)
    print(df)

def main():
    results_existing_format = process_urls(urls_existing_format, parse_existing_format)
    results_brunner_format = process_urls(urls_brunner_format, parse_brunner_format)
    
    all_results = results_existing_format + results_brunner_format
    display_results(all_results)

if __name__ == "__main__":
    main()
