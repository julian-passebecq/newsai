import csv
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

# Function to extract and format the article title from the URL
def extract_title(url):
    # Extract the last part of the URL and replace hyphens with spaces
    title_slug = url.rstrip('/').split('/')[-1]
    title = unquote(title_slug).replace('-', ' ').title()
    return title

# Function to get sitemap content from the URL
def get_sitemap_content(url):
    # Send a GET request to the sitemap URL
    response = requests.get(url)
    # Return the content of the response
    return response.content

# URL of the sitemap
sitemap_url = 'https://blog.crossjoin.co.uk/sitemap-1.xml'

# Get the sitemap content
sitemap_content = get_sitemap_content(sitemap_url)

# Parse the XML content
root = ET.fromstring(sitemap_content)

# Define the namespace map to avoid using the full namespace in the find/findall methods
namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

# Create a CSV file
with open('/sitemap.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['article', 'url', 'date'])  # Writing the header

    # Iterate over each URL in the XML
    for url in root.findall('sm:url', namespaces=namespaces):
        loc_element = url.find('sm:loc', namespaces=namespaces)
        lastmod_element = url.find('sm:lastmod', namespaces=namespaces)
        
        # Use the .text of the element if it exists, otherwise provide a default value
        loc = loc_element.text if loc_element is not None else 'No URL'
        lastmod = lastmod_element.text if lastmod_element is not None else 'Not provided'
        
        # Extract the article title from the URL
        article_title = extract_title(loc)
        
        # Write the data to the CSV file
        writer.writerow([article_title, loc, lastmod])

print("CSV file created successfully.")
