import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Extend the sitemap URLs with the new website
sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml'
}

def find_lastmod_element(url_element, namespace):
    # Check for the standard 'lastmod' tag first
    lastmod = url_element.find(f'{namespace}lastmod')
    if lastmod is not None:
        return lastmod.text
    
    # Add other site-specific last modified tag checks here if necessary
    
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
    namespace = {'': namespace}  # For use with find/findall

    articles = []
    for url_elem in sitemap_xml.findall('.//url', namespaces=namespace):
        loc = url_elem.find('.//loc', namespaces=namespace).text if url_elem.find('.//loc', namespaces=namespace) is not None else 'URL not found'
        lastmod = find_lastmod_element(url_elem, namespace)  # Now using the helper function
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
