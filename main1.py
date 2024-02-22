import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# List of websites to fetch sitemaps from, with their names and URLs
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
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
        article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
        article_name = article_name.replace('-', ' ')  # Replace hyphens with spaces
        data.append({
            'Website': website_name,
            'URL': loc,
            'Article Name': article_name,
            'Last Mod.': lastmod  # Keep as original for internal operations
        })
    return data

# Function to aggregate articles from multiple websites
def fetch_articles_from_websites(websites):
    all_articles = []
    for website in websites:
        website_articles = fetch_sitemap(website['url'], website['name'])
        all_articles.extend(website_articles)
    return all_articles

# Function to filter articles based on a search query
def filter_articles(articles, query):
    if not query:
        return articles
    return [article for article in articles if query.lower() in article['Article Name'].lower()]

# Main Streamlit app
def main():
    st.title('Article Search Across Multiple Websites')
    
    articles = fetch_articles_from_websites(websites)

    # Convert the articles list to a pandas DataFrame
    articles_df = pd.DataFrame(articles)
    # Ensure 'Last Mod.' is treated as datetime for internal operations
    articles_df['Last Mod.'] = pd.to_datetime(articles_df['Last Mod.'])

    search_query = st.text_input('Enter search term:', '')

    filtered_articles = filter_articles(articles, search_query)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        # Re-apply the datetime conversion to ensure 'Last Mod.' is always datetime
        filtered_df['Last Mod.'] = pd.to_datetime(filtered_df['Last Mod.'])
        # Sort by 'Last Mod.' to ensure sorting happens on the datetime column
        filtered_df = filtered_df.sort_values(by='Last Mod.', ascending=False)
        # Format the 'Last Mod.' column for display now that we're sure it's datetime
        filtered_df['Formatted Last Mod.'] = filtered_df['Last Mod.'].dt.strftime('%d %B %Y')
        # Display the DataFrame, including the internal 'Last Mod.' for operations and the formatted one for readability
        st.write(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.', 'Formatted Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
