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
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml'  # New website added
}

def find_lastmod_element(url_elem, namespace):
    lastmod_elem = url_elem.find(f'{namespace}lastmod')
    if lastmod_elem is not None:
        # Strip the text to remove any leading/trailing whitespace
        return lastmod_elem.text.strip()
    return 'Not provided'

def parse_sitemap(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    try:
        sitemap_xml = ET.fromstring(response.content)
        # Extract the namespace URL from the 'urlset' element (if present)
        namespace = sitemap_xml.tag.split('}')[0].strip('{') if '}' in sitemap_xml.tag else ''
        namespace = f'{{{namespace}}}' if namespace else ''  # Reformat to use with find/findall
    except ET.ParseError:
        return []

    articles = []
    for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
        loc_elem = url_elem.find(f'{namespace}loc')
        loc = loc_elem.text.strip() if loc_elem is not None else 'URL not found'
        lastmod = find_lastmod_element(url_elem, namespace)
        articles.append({'URL': loc, 'Last Modified': lastmod})

    return articles

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website_name, sitemap_url in sitemap_urls.items():
        articles = parse_sitemap(sitemap_url)
        for article in articles:
            article['Website'] = website_name
        all_articles.extend(articles)
    
    # Convert to DataFrame only if articles are present
    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        
        # Search functionality
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_articles = articles_df
        
        # Display results
        st.write(filtered_articles)
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
