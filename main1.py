import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Define the sitemap URLs
sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml'
}

def find_lastmod_element(url_elem, namespace):
    # Possible tag names for the last modified date
    for tag in ['lastmod', 'Last Modified', 'lastMod']:
        lastmod = url_elem.find(f'{namespace}{tag}')
        if lastmod is not None:
            return lastmod.text
    return 'Not provided'

def parse_sitemap(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    try:
        sitemap_xml = ET.fromstring(response.content)
    except ET.ParseError:
        return []

    # Look for the namespace
    namespace = ''
    if '}' in sitemap_xml.tag:
        namespace = sitemap_xml.tag.split('}')[0] + '}'

    articles = []
    for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
        loc = url_elem.find(f'{namespace}loc').text if url_elem.find(f'{namespace}loc') is not None else 'URL not found'
        lastmod = find_lastmod_element(url_elem, namespace)  # Use the new function to find the last modified date
        articles.append({'URL': loc, 'Last Modified': lastmod})

    return articles

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website_name, sitemap_url in sitemap_urls.items():
        articles = parse_sitemap(sitemap_url)
        for article in articles:
            article['Website'] = website_name  # Add website name to each article
        all_articles.extend(articles)
    
    articles_df = pd.DataFrame(all_articles)
    articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)

    search_query = st.text_input('Enter search term:')
    if search_query:
        filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_articles = articles_df

    st.write(filtered_articles)

if __name__ == "__main__":
    main()
