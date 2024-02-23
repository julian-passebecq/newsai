import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Define the sitemap URLs including Brunner
sitemap_urls = {
    'Kevin R Chant': 'https://www.kevinrchant.com/post-sitemap.xml',
    'Data Mozart': 'https://data-mozart.com/post-sitemap.xml',
    'Crossjoin': 'https://blog.crossjoin.co.uk/sitemap-1.xml',
    'Thomas Leblanc': 'https://thomas-leblanc.com/sitemap-1.xml',
    'Brunner': 'https://en.brunner.bi/blog-posts-sitemap.xml',
}

# Function to fetch and parse the sitemap XML
def fetch_parse_sitemap(url):
    try:
        # Fetch the XML content
        response = requests.get(url)
        response.raise_for_status()  # will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        st.error(f"Request error for {url}: {e}")
        return []
    try:
        # Parse the XML content
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        # Find all 'url' elements
        urls = root.findall('ns:url', namespace)
        articles = [
            {
                'URL': elem.find('ns:loc', namespace).text,
                'Last Modified': elem.find('ns:lastmod', namespace).text if elem.find('ns:lastmod', namespace) is not None else 'Not provided'
            }
            for elem in urls
        ]
        return articles
    except ET.ParseError as e:
        st.error(f"XML parse error for {url}: {e}")
        return []

# Main function to run the Streamlit app
def main():
    st.title('Article Search Across Multiple Websites')
    all_articles = []
    for name, url in sitemap_urls.items():
        articles = fetch_parse_sitemap(url)
        # Add the website name to each article
        for article in articles:
            article['Website'] = name
        all_articles.extend(articles)
    # Create a DataFrame from the articles
    df = pd.DataFrame(all_articles)
    # Convert 'Last Modified' to datetime and format it
    df['Last Modified'] = pd.to_datetime(df['Last Modified'], errors='coerce').dt.strftime('%Y-%m-%d')

    # User input for search
    search_query = st.text_input('Enter search term:')
    # Filter articles based on search query
    filtered_articles = df[df['URL'].str.contains(search_query, na=False)] if search_query else df

    # Display the articles in the app
    st.dataframe(filtered_articles)

if __name__ == "__main__":
    main()
