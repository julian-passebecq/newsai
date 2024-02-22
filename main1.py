import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Define websites with their names and sitemap URLs
websites = [
    {'name': 'Kevin R Chant', 'url': 'https://www.kevinrchant.com/post-sitemap.xml'},
    {'name': 'Data Mozart', 'url': 'https://data-mozart.com/post-sitemap.xml'},
    {'name': 'Crossjoin', 'url': 'https://blog.crossjoin.co.uk/sitemap-1.xml'},
    {'name': 'Thomas Leblanc', 'url': 'https://thomas-leblanc.com/sitemap-1.xml'}
]

# Function to fetch and parse the sitemap
def fetch_sitemap(url, website_name):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    data = []
    
    # Different handling based on the website
    if "kevinrchant.com" in url or "data-mozart.com" in url:
        # Process sitemaps that follow a specific structure
        for sitemap_url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = sitemap_url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            lastmod = sitemap_url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            lastmod = lastmod.text if lastmod is not None else 'Unknown'
            article_name = loc.split('/')[-1].replace('-', ' ')
            data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod})
    else:
        # Handle other sitemaps without specific namespaces
        for sitemap_url in root.findall('.//url'):
            loc = sitemap_url.find('.//loc').text
            lastmod = sitemap_url.find('.//lastmod')
            lastmod = lastmod.text if lastmod is not None else 'Unknown'
            article_name = loc.split('/')[-1].replace('-', ' ')
            data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod})
    return data

# Function to aggregate articles from multiple websites
def fetch_articles_from_websites(websites):
    all_articles = []
    for website in websites:
        articles = fetch_sitemap(website['url'], website['name'])
        all_articles.extend(articles)
    return all_articles

# Function to filter articles based on a search query
def filter_articles(articles, query):
    if not query:
        return articles
    return [article for article in articles if query.lower() in article['Article Name'].lower()]

# Main Streamlit app logic
def main():
    st.title('Article Search Across Multiple Websites')
    
    articles = fetch_articles_from_websites(websites)
    articles_df = pd.DataFrame(articles)
    articles_df['Last Mod.'] = pd.to_datetime(articles_df['Last Mod.'])

    search_query = st.text_input('Enter search term:')
    filtered_articles = filter_articles(articles, search_query)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        filtered_df['Last Mod.'] = pd.to_datetime(filtered_df['Last Mod.'])
        filtered_df = filtered_df.sort_values(by='Last Mod.', ascending=False)
        st.write(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
