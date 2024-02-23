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
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml',
}

def parse_sitemap(url):
    try:
        response = requests.get(url)
        # Check if we got a successful response from the server
        if response.status_code == 200:
            # Define the namespace
            namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
            ns_map = {'ns': namespace}
            sitemap_xml = ET.fromstring(response.content)
            articles = []
            for url_elem in sitemap_xml.findall('ns:url', ns_map):
                loc = url_elem.find('ns:loc', ns_map).text
                lastmod_elem = url_elem.find('ns:lastmod', ns_map)
                lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
                if lastmod != 'Not provided':
                    try:
                        lastmod = parser.parse(lastmod).isoformat()
                    except ValueError:
                        lastmod = 'Invalid date format'
                articles.append({'URL': loc, 'Last Modified': lastmod})
            return articles
        else:
            st.error(f"Error fetching {url}: Status code {response.status_code}")
            return []
    except requests.RequestException as e:
        st.error(f"Request failed for {url}: {e}")
        return []
    except ET.ParseError as e:
        st.error(f"XML parsing error for {url}: {e}")
        return []

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website_name, sitemap_url in sitemap_urls.items():
        st.write(f"Fetching articles from: {sitemap_url}")  # Display on Streamlit app
        articles = parse_sitemap(sitemap_url)
        if articles:
            for article in articles:
                article['Website'] = website_name
            all_articles.extend(articles)
    
    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        if 'Last Modified' in articles_df:
            articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
            st.write(filtered_articles)
        else:
            st.write(articles_df)
    else:
        st.error("No articles were found. Please check the sitemap URLs.")

if __name__ == "__main__":
    main()
