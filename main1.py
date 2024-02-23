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

# Function to find the lastmod element based on possible different tag names
def find_lastmod_element(url_element):
    for tag in ['lastmod', 'Last Modified', 'lastMod']:
        lastmod = url_element.find(f'.//{tag}')
        if lastmod is not None:
            return lastmod.text
    return 'Unknown'

# Function to fetch and parse the sitemap
def fetch_sitemap(url, website_name):
    try:
        response = requests.get(url)
        if 'xml' not in response.headers.get('Content-Type', ''):
            print(f"Non-XML content for {website_name} at {url}")
            return []

        root = ET.fromstring(response.content)
        data = []
        for sitemap_url in root.findall('.//url'):
            loc = sitemap_url.find('.//loc').text
            lastmod = find_lastmod_element(sitemap_url)
            article_name = loc.split('/')[-1].replace('-', ' ').replace('.html', '').replace('.htm', '')
            data.append({'Website': website_name, 'URL': loc, 'Article Name': article_name, 'Last Mod.': lastmod})
    except ET.ParseError as e:
        print(f"XML parsing error for {website_name} at {url}: {e}")
        return []
    except Exception as e:
        print(f"Error fetching or parsing sitemap for {website_name} at {url}: {e}")
        return []

    return data

# Main function to fetch and display articles
