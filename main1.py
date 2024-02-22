import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# Adjust the headers for requests to handle servers that might reject the default Python requests User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to fetch and parse the sitemap
def fetch_sitemap(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error for bad responses
        root = ET.fromstring(response.content)
        data = []
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url in root.findall('sitemap:url/sitemap:loc', namespace) + root.findall('sitemap:url', namespace):
            loc = url.text if url.text else url.find('sitemap:loc', namespace).text
            lastmod = url.find('sitemap:lastmod', namespace)
            lastmod = lastmod.text if lastmod is not None else "Unknown"
            article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
            article_name = article_name.replace('-', ' ')  # Replace dashes with spaces
            website_name = urlparse(loc).netloc  # Extract website name from URL

            # Attempt to parse and format the lastmod date
            try:
                if lastmod != "Unknown":
                    lastmod_datetime = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S%z")
                    lastmod_formatted = lastmod_datetime.strftime('%d %B %Y')
                else:
                    lastmod_formatted = "Unknown"
            except ValueError:
                # Handle different date formats if necessary
                lastmod_formatted = "Unknown"

            data.append({
                'Website': website_name,
                'URL': loc,
                'Article Name': article_name,
                'Last Mod.': lastmod_formatted
            })
        return data
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return []
    except ET.ParseError as e:
        print(f"XML parse error for {url}: {e}")
        return []

# Function to fetch articles from multiple sitemaps
def fetch_multiple_sitemaps(urls):
    articles = []
    for url in urls:
        articles.extend(fetch_sitemap(url))
    return articles

# Function to filter articles based on a search query and website
def filter_articles(articles, query, website):
    filtered_articles = articles
    if query:
        filtered_articles = [article for article in filtered_articles if query.lower() in article['Article Name'].lower()]
    if website and website != 'All':
        filtered_articles = [article for article in filtered_articles if website.lower() == article['Website'].lower()]
    return filtered_articles

# Main Streamlit app
def main():
    st.title('Article Search Across Multiple Sites')

    sitemap_urls = [
        'https://www.kevinrchant.com/post-sitemap.xml',
        'https://data-mozart.com/post-sitemap.xml',
        'https://thomas-leblanc.com/sitemap-1.xml',
        'https://www.oliviertravers.com/post-sitemap.xml',
    ]

    articles = fetch_multiple_sitemaps(sitemap_urls)

    articles_df = pd.DataFrame(articles)

    search_query = st.text_input('Enter search term:')
    website_option = st.selectbox('Select website', ['All'] + sorted(set(articles_df['Website'])))

    filtered_articles = filter_articles(articles, search_query, website_option)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        st.dataframe(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.']], height=600)
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
