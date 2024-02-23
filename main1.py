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
    'Brunner BI': 'https://en.brunner.bi/blog-posts-sitemap.xml'
}

def parse_sitemap(url, is_brunner_format):
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Error fetching the sitemap: HTTP {response.status_code}")
        return []
    
    try:
        sitemap_xml = ET.fromstring(response.content)
    except ET.ParseError as e:
        st.error(f"XML parsing error: {e}")
        return []
    
    namespace = ''
    if not is_brunner_format and '}' in sitemap_xml.tag:
        namespace = sitemap_xml.tag.split('}')[0] + '}'
    
    articles = []
    for url_elem in sitemap_xml.findall('.//{}url'.format(namespace)):
        loc = url_elem.find('{}loc'.format(namespace)).text
        lastmod_elem = url_elem.find('{}lastmod'.format(namespace)) if not is_brunner_format else url_elem.find('lastmod')
        lastmod = lastmod_elem.text if lastmod_elem is not None else 'Not provided'
        if is_brunner_format and lastmod != 'Not provided':
            try:
                lastmod = parser.parse(lastmod).isoformat()
            except ValueError:
                lastmod = 'Invalid date format'
        articles.append({'URL': loc, 'Last Modified': lastmod})
    return articles

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website, sitemap_url in sitemap_urls.items():
        is_brunner_format = website == 'Brunner BI'
        articles = parse_sitemap(sitemap_url, is_brunner_format)
        for article in articles:
            article['Website'] = website
        all_articles.extend(articles)
    
    articles_df = pd.DataFrame(all_articles)
    articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)

    # Multi-select filter for websites
    website_selection = st.multiselect('Select Websites', options=list(sitemap_urls.keys()), default=list(sitemap_urls.keys()))
    filtered_df = articles_df[articles_df['Website'].isin(website_selection)]
    
    search_query = st.text_input('Enter search term:')
    if search_query:
        filtered_df = filtered_df[filtered_df['URL'].str.contains(search_query, case=False, na=False)]

    st.write(filtered_df)

if __name__ == "__main__":
    main()
