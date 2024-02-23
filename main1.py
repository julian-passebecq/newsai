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
        if response.status_code == 200:
            sitemap_xml = ET.fromstring(response.content)
            articles = []

            # Check for the presence of a namespace.
            namespace = ''
            for elem in sitemap_xml.iter():
                if '}' in elem.tag:
                    namespace = elem.tag.split('}')[0] + '}'
                    break

            # Find all 'url' elements in the XML
            for url_elem in sitemap_xml.findall(f'.//{namespace}url'):
                loc = url_elem.find(f'{namespace}loc').text
                lastmod_elem = url_elem.find(f'{namespace}lastmod')
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
        articles = parse_sitemap(sitemap_url)
        if articles:
            for article in articles:
                article['Website'] = website_name
            all_articles.extend(articles)
    
    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        if 'Last Modified' in articles_df.columns:
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
