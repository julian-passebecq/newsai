import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# Helper function to normalize namespace prefixes and find elements
def find_with_ns(element, tag, namespaces):
    # Try to find the element with provided namespaces
    for ns in namespaces:
        found = element.find(f'.//{{{ns}}}{tag}')
        if found is not None:
            return found
    return None

# Function to fetch and parse the sitemap, with enhanced error handling and date parsing
def fetch_sitemap(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This ensures HTTP errors are caught
        # Attempt to parse the XML content
        root = ET.fromstring(response.content)
        data = []
        # Define common namespaces that might be used in sitemaps
        namespaces = ['http://www.sitemaps.org/schemas/sitemap/0.9', 'http://www.google.com/schemas/sitemap/0.84']
        for sitemap in root.findall('.//{*}url'):
            loc = sitemap.find(f'.//{{*}}loc').text
            lastmod_element = find_with_ns(sitemap, 'lastmod', namespaces)
            lastmod = lastmod_element.text if lastmod_element is not None else "Unknown"
            article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
            article_name = article_name.replace('-', ' ')  # Convert URL slug to readable format
            website_name = urlparse(loc).netloc  # Extract website domain
            
            # Attempt to parse and format the last modification date
            if lastmod != "Unknown":
                try:
                    # Handling different date formats
                    if '+' in lastmod:
                        lastmod_datetime = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S%z")
                    else:
                        lastmod_datetime = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S")
                    lastmod_formatted = lastmod_datetime.strftime('%d %B %Y')
                except ValueError:
                    # Fallback if the date format does not match expectations
                    lastmod_formatted = "Unknown"
            else:
                lastmod_formatted = "Unknown"
            
            data.append({
                'Website': website_name,
                'URL': loc,
                'Article Name': article_name,
                'Last Mod.': lastmod_formatted
            })
        return data
    except requests.RequestException as e:
        st.error(f"Request error for {url}: {e}")
        return []
    except ET.ParseError as e:
        st.error(f"XML parse error for {url}: {e}")
        return []


# Fetch articles from multiple sitemaps
def fetch_multiple_sitemaps(urls):
    articles = []
    for url in urls:
        articles.extend(fetch_sitemap(url))
    return articles

# Filter articles based on search query and website
def filter_articles(articles, query, website):
    filtered_articles = articles
    if query:
        filtered_articles = [article for article in filtered_articles if query.lower() in article['Article Name'].lower()]
    if website:
        filtered_articles = [article for article in filtered_articles if website.lower() in article['Website'].lower()]
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
    website_option = st.selectbox('Select website', options=['All'] + sorted(list(set(articles_df['Website']))))

    if website_option and website_option != 'All':
        filtered_articles = filter_articles(articles, search_query, website_option)
    else:
        filtered_articles = filter_articles(articles, search_query, '')

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        st.dataframe(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.']], height=600)
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
