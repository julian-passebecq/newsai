import requests
import xml.etree.ElementTree as ET
import pandas as pd
from dateutil import parser

def parse_brunner_sitemap(url):
    # Get the XML content from the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching the sitemap: HTTP {response.status_code}")
        return []
    
    # Parse the XML content
    try:
        # Define the namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Parse the XML with the namespace
        sitemap_xml = ET.fromstring(response.content)
        articles = []
        
        # Find all 'url' elements in the XML
        for url_elem in sitemap_xml.findall('ns:url', namespace):
            # Extract the 'loc' and 'lastmod' elements using the namespace
            loc = url_elem.find('ns:loc', namespace).text
            lastmod = url_elem.find('ns:lastmod', namespace).text
            
            # Attempt to parse the 'lastmod' date
            try:
                lastmod = parser.parse(lastmod).isoformat()
            except ValueError:
                lastmod = 'Invalid date format'
                
            # Append the extracted information to the articles list
            articles.append({'URL': loc, 'Last Modified': lastmod})
            
        return articles
    
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return []

# Brunner BI sitemap URL
brunner_sitemap_url = 'https://en.brunner.bi/blog-posts-sitemap.xml'

# Parse the Brunner BI sitemap
brunner_articles = parse_brunner_sitemap(brunner_sitemap_url)

# Convert the articles list to a DataFrame
brunner_articles_df = pd.DataFrame(brunner_articles)
print(brunner_articles_df)
