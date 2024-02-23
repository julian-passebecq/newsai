import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from dateutil import parser

# Arrays to hold different types of sitemap URLs
standard_sitemap_urls = [
    'https://www.kevinrchant.com/post-sitemap.xml',
    'https://data-mozart.com/post-sitemap.xml',
    'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'https://thomas-leblanc.com/sitemap-1.xml',
    # Add more standard sitemaps here
]

brunner_sitemap_urls = [
    'https://en.brunner.bi/blog-posts-sitemap.xml',
    # Add more Brunner format sitemaps here
]

def parse_standard_sitemap(url):
    """Parse sitemaps with the standard format."""
    response = requests.get(url)
    if response.status_code != 200:
        return []
    try:
        sitemap_xml = ET.fromstring(response.content)
    except ET.ParseError:
        return []

    namespace = ''
    if '}' in sitemap_xml.tag:
        namespace = sitemap_xml.tag.split('}')[0] + '}'

    articles = []
    for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
        loc = url_elem.find(f'{namespace}loc').text if url_elem.find(f'{namespace}loc') is not None else 'URL not found'
        lastmod_elem = url_elem.find(f'{namespace}lastmod')
        lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
        articles.append({'URL': loc, 'Last Modified': lastmod})

    return articles

def parse_brunner_sitemap(url):
    """Parse sitemaps with the Brunner format."""
    response = requests.get(url)
    if response.status_code != 200:
        return []

    try:
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemap_xml = ET.fromstring(response.content)
        articles = []
        for url_elem in sitemap_xml.findall('ns:url', namespace):
            loc = url_elem.find('ns:loc', namespace).text
            lastmod_elem = url_elem.find('ns:lastmod', namespace)
            lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
            if lastmod != 'Not provided':
                try:
                    lastmod = parser.parse(lastmod).isoformat()
                except ValueError:
                    lastmod = 'Invalid date format'
            articles.append({'URL': loc, 'Last Modified': lastmod})
        return articles
    except ET.ParseError:
        return []

def main():
    st.title('Article Search Across Multiple Websites')

    all_articles = []
    # Process standard format sitemaps
    for url in standard_sitemap_urls:
        articles = parse_standard_sitemap(url)
        all_articles.extend(articles)

    # Process Brunner format sitemaps
    for url in brunner_sitemap_urls:
        articles = parse_brunner_sitemap(url)
        all_articles.extend(articles)

    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
            st.write(filtered_articles)
        else:
            st.write(articles_df)
    else:
        st.error("No articles were found. Please check the sitemap URLs.")

if __name__ == "__main__":
    main()
