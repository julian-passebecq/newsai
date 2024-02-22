import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Function to fetch and parse the sitemap, now includes website name
def fetch_sitemap(url, website_name='Default Website'):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    data = []
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
        article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
        article_name = article_name.replace('-', ' ')  # Replace hyphens with spaces
        # Assume category is the second to last path segment; adjust as necessary
        category = loc.split('/')[-3] if loc.endswith('/') else loc.split('/')[-2]
        data.append({
            'Website': website_name,
            'Category': category,  # Added category
            'URL': loc,
            'Article Name': article_name,
            'Last Mod.': lastmod
        })
    return data

# Function to filter articles based on a search query
def filter_articles(articles, query):
    if not query:
        return articles
    return [article for article in articles if query.lower() in article['Article Name'].lower()]

# Main Streamlit app
def main():
    st.title('Article Search')
    sitemap_url = 'https://www.kevinrchant.com/post-sitemap.xml'
    articles = fetch_sitemap(sitemap_url, 'Kevin R Chant')  # Added website name

    # Convert the articles list to a pandas DataFrame
    articles_df = pd.DataFrame(articles)
    # Ensure 'Last Mod.' is treated as datetime
    articles_df['Last Mod.'] = pd.to_datetime(articles_df['Last Mod.'])

    search_query = st.text_input('Enter search term:', '')

    filtered_articles = filter_articles(articles, search_query)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        # Ensure 'Last Mod.' in filtered_df is also datetime to avoid the AttributeError
        filtered_df['Last Mod.'] = pd.to_datetime(filtered_df['Last Mod.'])
        # Sort by 'Last Mod.'
        filtered_df = filtered_df.sort_values(by='Last Mod.', ascending=False)
        # Format the 'Last Mod.' column for display
        filtered_df['Formatted Last Mod.'] = filtered_df['Last Mod.'].dt.strftime('%d %B %Y')
        st.write(filtered_df[['Website', 'Category', 'Article Name', 'URL', 'Formatted Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
