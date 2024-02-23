import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Define the sitemap URLs including Brunner
sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    'Brunner': 'https://en.brunner.bi/blog-posts-sitemap.xml',  # Added Brunner sitemap
    # Add more sitemaps here as needed
}

# Namespace dictionary to handle namespaces in XML tags
namespaces = {
    '': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'news': 'http://www.google.com/schemas/sitemap-news/0.9',
    # Add other namespaces if needed
}

def parse_sitemap(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    try:
        # Register namespaces and parse the XML
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)
        sitemap_xml = ET.fromstring(response.content)
    except ET.ParseError:
        return []

    articles = []
    for url_elem in sitemap_xml.findall('url', namespaces):
        loc = url_elem.find('loc', namespaces).text if url_elem.find('loc', namespaces) is not None else 'URL not found'
        lastmod = url_elem.find('lastmod', namespaces).text if url_elem.find('lastmod', namespaces) is not None else 'Not provided'
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
    
    articles_df = pd.DataFrame(all_articles)
    articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True).dt.strftime('%Y-%m-%d')

    search_query = st.text_input('Enter search term:')
    if search_query:
        filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_articles = articles_df

    st.write(filtered_articles)

if __name__ == "__main__":
    main()
