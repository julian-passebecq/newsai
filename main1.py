import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from dateutil import parser

# Define the sitemap URLs
sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml',  # Added the new website here
}

def parse_sitemap(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch sitemap from {url}, status code: {response.status_code}")
        return []
    try:
        namespace = ''  # Default namespace
        if '}' in response.content.decode('utf-8'):
            namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        
        sitemap_xml = ET.fromstring(response.content)
        articles = []
        for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
            loc = url_elem.find(f'{namespace}loc').text if url_elem.find(f'{namespace}loc') is not None else 'URL not found'
            lastmod = 'Not provided'
            lastmod_elem = url_elem.find(f'{namespace}lastmod')
            if lastmod_elem is not None:
                lastmod = lastmod_elem.text
                try:
                    lastmod = parser.parse(lastmod).isoformat()
                except ValueError:
                    lastmod = 'Invalid date format'
            articles.append({'URL': loc, 'Last Modified': lastmod})
        
        return articles

    except ET.ParseError as e:
        print(f"XML parsing error for {url}: {e}")
        return []

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website_name, sitemap_url in sitemap_urls.items():
        print(f"Fetching articles from: {sitemap_url}")
        articles = parse_sitemap(sitemap_url)
        if articles:
            print(f"Found {len(articles)} articles in {sitemap_url}")
            for article in articles:
                article['Website'] = website_name
            all_articles.extend(articles)
        else:
            print(f"No articles found in {sitemap_url}")

    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        if 'Last Modified' in articles_df.columns:
            articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        else:
            st.error("The 'Last Modified' column was not found in the articles data.")
            return
        
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_articles = articles_df

        st.write(filtered_articles)
    else:
        st.error("No articles were found. Please check the sitemap URLs.")

if __name__ == "__main__":
    main()
