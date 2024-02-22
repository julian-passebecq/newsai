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

def fetch_sitemap(url, website_name):
    try:
        response = requests.get(url)
        # Basic check for XML content type, may need adjustment based on actual response
        if 'xml' not in response.headers.get('Content-Type', ''):
            print(f"Non-XML content for {website_name} at {url}")
            return []

        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML parsing error for {website_name} at {url}: {e}")
        return []
    except Exception as e:
        print(f"Error fetching or parsing sitemap for {website_name} at {url}: {e}")
        return []

    data = []
    # Adjust paths based on sitemap structure
    for sitemap_url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url') or root.findall('.//url'):
        loc = sitemap_url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc') or sitemap_url.find('.//loc')
        loc = loc.text if loc is not None else 'Unknown URL'
        lastmod = sitemap_url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod') or sitemap_url.find('.//lastmod')
        lastmod = lastmod.text if lastmod is not None else 'Unknown'
        article_name = loc.split('/')[-1].replace('-', ' ')
        data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod})

    return data

def fetch_articles_from_websites(websites):
    all_articles = []
    for website in websites:
        articles = fetch_sitemap(website['url'], website['name'])
        all_articles.extend(articles)
    return all_articles

def filter_articles(articles, query):
    if not query:
        return articles
    return [article for article in articles if query.lower() in article['Article Name'].lower()]

def main():
    st.title('Article Search Across Multiple Websites')
    
    articles = fetch_articles_from_websites(websites)
    articles_df = pd.DataFrame(articles)
    articles_df['Last Mod.'] = pd.to_datetime(articles_df['Last Mod.'], errors='coerce')

    search_query = st.text_input('Enter search term:')
    filtered_articles = filter_articles(articles, search_query)

    if filtered_articles:
        filtered_df = pd.DataFrame(filtered_articles)
        filtered_df = filtered_df.sort_values(by='Last Mod.', ascending=False)
        st.write(filtered_df[['Website', 'Article Name', 'URL', 'Last Mod.']])
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
