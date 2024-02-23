import streamlit as st
from usp.tree import sitemap_tree_for_homepage
import pandas as pd

# List of websites to fetch sitemap information from
websites = [
    'https://www.kevinrchant.com',
    'https://data-mozart.com',
    'https://blog.crossjoin.co.uk',
    'https://thomas-leblanc.com',
    'https://en.brunner.bi',
]

def get_sitemap_data(website):
    """Fetch sitemap data from a website and return a list of dictionaries."""
    try:
        tree = sitemap_tree_for_homepage(website)
        pages_data = [{
            'URL': page.url,
            'Last Modified': page.last_modified,
            'Website': website
        } for page in tree.all_pages()]
        return pages_data
    except Exception as e:
        st.error(f"Failed to fetch sitemap from {website}: {e}")
        return []

def main():
    st.title('Sitemap Article Search')

    # Fetch sitemap data for all websites and combine into a single list
    all_sitemap_data = []
    for website in websites:
        sitemap_data = get_sitemap_data(website)
        all_sitemap_data.extend(sitemap_data)

    # Convert the combined sitemap data into a pandas DataFrame
    sitemap_df = pd.DataFrame(all_sitemap_data)
    sitemap_df['Last Modified'] = pd.to_datetime(sitemap_df['Last Modified'], errors='coerce').dt.date  # Convert to just date for simplicity

    # Display the DataFrame in Streamlit
    if not sitemap_df.empty:
        # Multi-select box for filtering by website
        selected_websites = st.multiselect('Select Websites', options=websites, default=websites)
        filtered_sitemap_df = sitemap_df[sitemap_df['Website'].isin(selected_websites)]

        # Text input for search query
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_sitemap_df = filtered_sitemap_df[filtered_sitemap_df['URL'].str.contains(search_query, case=False, na=False)]

        # Display the filtered DataFrame
        st.dataframe(filtered_sitemap_df)
    else:
        st.write("No sitemap data available.")

if __name__ == "__main__":
    main()
