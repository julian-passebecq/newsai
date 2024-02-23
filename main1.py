import streamlit as st
import requests
import xml.etree.ElementTree as ET
from dateutil import parser
import pandas as pd

# Define the sitemap URLs for standard and Brunner format
standard_sitemap_urls = [
    'https://www.kevinrchant.com/post-sitemap.xml',
    'https://data-mozart.com/post-sitemap.xml',
    'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'https://thomas-leblanc.com/sitemap-1.xml',
]

brunner_sitemap_url = 'https://en.brunner.bi/blog-posts-sitemap.xml'

def parse_standard_sitemap(url):
    """Parse sitemaps with the standard format."""
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Error fetching the sitemap from {url}: HTTP {response.status_code}")
        return []
    
    try:
        sitemap_xml = ET.fromstring(response.content)
    except ET.ParseError as e:
        st.error(f"XML parsing error for {url}: {e}")
        return []

    namespace = ''
    if '}' in sitemap_xml.tag:
        namespace = sitemap_xml.tag.split('}')[0] + '}'

    articles = []
    for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
        loc = url_elem.find(f'{namespace}loc').text
        lastmod_elem = url_elem.find(f'{namespace}lastmod')
        lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
        articles.append({'URL': loc, 'Last Modified': lastmod, 'Website': url.split('/')[2]})
    return articles

def parse_brunner_sitemap(url):
    """Parse sitemaps with the Brunner format."""
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Error fetching the sitemap from {url}: HTTP {response.status_code}")
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
            articles.append({'URL': loc, 'Last Modified': lastmod, 'Website': 'Brunner BI'})
        return articles
    except ET.ParseError as e:
        st.error(f"XML parsing error for {url}: {e}")
        return []

def main():
    st.title('Article Search Across Multiple Websites')

    all_articles = []
    # Process standard format sitemaps
    for sitemap_url in standard_sitemap_urls:
        articles = parse_standard_sitemap(sitemap_url)
        all_articles.extend(articles)

    # Process Brunner format sitemap
    brunner_articles = parse_brunner_sitemap(brunner_sitemap_url)
    all_articles.extend(brunner_articles)

    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        
        # Multi-select filter for websites
        websites = list(set(articles_df['Website']))
        website_selection = st.multiselect('Select Websites', options=websites, default=websites)
        filtered_df = articles_df[articles_df['Website'].isin(website_selection)]
        
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_df = filtered_df[filtered_df['URL'].str.contains(search_query, case=False, na=False)]
        
        st.write(filtered_df)
    else:
        st.error("No articles were found. Please check the sitemap URLs.")

if __name__ == "__main__":
    main()
