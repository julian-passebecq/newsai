import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Function to fetch and parse the sitemap
def fetch_sitemap(url, website_name):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    data = []
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
        article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
        # Replace dashes with spaces for the article name
        article_name = article_name.replace('-', ' ')
        # Format the date to "day month year"
        lastmod_formatted = datetime.strptime(lastmod.split('T')[0], '%Y-%m-%d').strftime('%d %B %Y')
        data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod_formatted})
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
    website_name = 'Kevin R Chant'  # Example website name, adjust as necessary
    articles = fetch_sitemap(sitemap_url, website_name)

    # Convert the articles list to a pandas DataFrame
    articles_df = pd.DataFrame(articles)

    search_query = st.text_input('Enter search term:', '')

    filtered_articles = filter_articles(articles, search_query)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        # Display the DataFrame with the new column order including website name
        st.write(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
