import streamlit as st
import requests
import xml.etree.ElementTree as ET
from dateutil import parser
import pandas as pd

# Define the sitemap URLs for standard and Brunner format
standard_sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    # Add more standard sitemaps here
}

brunner_sitemap_urls = {
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml',
    # Add more Brunner format sitemaps here
}

def parse_sitemap(url, is_brunner_format=False):
    """Parse sitemaps with the standard or Brunner format."""
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Error fetching the sitemap from {url}: HTTP {response.status_code}")
        return []

    try:
        sitemap_xml = ET.fromstring(response.content)
        articles = []

        if is_brunner_format:
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            url_tag = 'ns:url'
            loc_tag = 'ns:loc'
            lastmod_tag = 'ns:lastmod'
        else:
            namespace = {}
            url_tag = 'url'
            loc_tag = 'loc'
            lastmod_tag = 'lastmod'

        for url_elem in sitemap_xml.findall(url_tag, namespace):
            loc = url_elem.find(loc_tag, namespace).text
            lastmod_elem = url_elem.find(lastmod_tag, namespace)
            lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
            if is_brunner_format and lastmod != 'Not provided':
                try:
                    lastmod = parser.parse(lastmod).isoformat()
                except ValueError:
                    lastmod = 'Invalid date format'
            articles.append({'URL': loc, 'Last Modified': lastmod})
        return articles
    except ET.ParseError as e:
        st.error(f"XML parsing error for {url}: {e}")
        return []

def main():
    st.title('Article Search Across Multiple Websites')

    all_articles = []
    # Process standard format sitemaps
    for website, url in standard_sitemap_urls.items():
        articles = parse_sitemap(url)
        for article in articles:
            article['Website'] = website
        all_articles.extend(articles)

    # Process Brunner format sitemaps
    for website, url in brunner_sitemap_urls.items():
        articles = parse_sitemap(url, is_brunner_format=True)
        for article in articles:
            article['Website'] = website
        all_articles.extend(articles)

    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)

        # Multi-select filter for websites
        website_options = list(standard_sitemap_urls.keys()) + list(brunner_sitemap_urls.keys())
        website_selection = st.multiselect('Select Websites', options=website_options, default=website_options)
        filtered_df = articles_df[articles_df['Website'].isin(website_selection)]

        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_df = filtered_df[filtered_df['URL'].str.contains(search_query, case=False, na=False)]

        st.write(filtered_df)
    else:
        st.error("No articles were found. Please check the sitemap URLs.")

if __name__ == "__main__":
    main()
