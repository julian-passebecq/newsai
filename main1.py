import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Function to fetch and parse the sitemap, with website name included
def fetch_sitemap(url):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    data = []
    website_name = url.split('/')[2]  # Extract the website name from the URL
    for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        lastmod = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
        article_name = loc.split('/')[-2] if loc.endswith('/') else loc.split('/')[-1]
        # Replace dashes with spaces in the article name for correct syntax
        article_name = article_name.replace('-', ' ')
        # Format date
        lastmod_formatted = pd.to_datetime(lastmod).strftime('%d %B %Y')
        data.append({
            'Website': website_name,
            'URL': loc,
            'Article Name': article_name,
            'Last Mod.': lastmod_formatted
        })
    return data

# Fetch and combine sitemaps from multiple websites
def fetch_multiple_sitemaps(urls):
    all_articles = []
    for url in urls:
        articles = fetch_sitemap(url)
        all_articles.extend(articles)
    return all_articles

# Main Streamlit app
def main():
    st.title('Article Search Across Multiple Sites')
    
    # List of sitemaps to fetch articles from
    sitemap_urls = [
        'https://www.kevinrchant.com/post-sitemap.xml',
        'https://data-mozart.com/post-sitemap.xml',
        'https://thomas-leblanc.com/sitemap-1.xml',
        'https://www.oliviertravers.com/post-sitemap.xml'
    ]
    
    articles = fetch_multiple_sitemaps(sitemap_urls)
    articles_df = pd.DataFrame(articles)

    # Website filter
    website_list = articles_df['Website'].unique().tolist()
    selected_website = st.selectbox('Select a website to filter:', ['All'] + website_list)

    # Apply website filter if not 'All'
    if selected_website != 'All':
        articles_df = articles_df[articles_df['Website'] == selected_website]

    search_query = st.text_input('Enter search term:', '')

    # Filter articles based on the search query
    if search_query:
        articles_df = articles_df[articles_df['Article Name'].str.contains(search_query, case=False)]

    if not articles_df.empty:
        st.write(articles_df[['Website', 'Article Name', 'URL', 'Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
