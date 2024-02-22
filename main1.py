import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# Helper function to normalize namespace prefixes
def ns(tag):
    # Extract the namespace from the tag
    if '}' in tag:
        ns_uri, tag = tag.split('}')
        return f"{{{ns_uri[1:]}}}{tag}"
    return tag

# Function to fetch and parse the sitemap, with error handling and support for different XML structures
def fetch_sitemap(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for bad responses
        root = ET.fromstring(response.content)
        data = []
        for sitemap in root.findall('.//*'):
            if ns('loc') in sitemap.tag:
                loc = sitemap.text
                lastmod_tag = sitemap.find(f'.//{ns("lastmod")}')
                lastmod = lastmod_tag.text if lastmod_tag is not None else "Unknown"
                article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
                article_name = article_name.replace('-', ' ')  # Replace dashes with spaces for article name
                website_name = urlparse(loc).netloc  # Extract website name from URL
                
                # Parse and format the date
                if lastmod != "Unknown":
                    try:
                        lastmod_datetime = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S%z")
                        lastmod_formatted = lastmod_datetime.strftime('%d %B %Y')
                    except ValueError:
                        lastmod_formatted = "Unknown"
                else:
                    lastmod_formatted = "Unknown"
                
                data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod_formatted})
        return data
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return []
    except ET.ParseError as e:
        print(f"XML parse error for {url}: {e}")
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
