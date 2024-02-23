import streamlit as st
import pandas as pd
import numpy as np

# Load the CSV data into a DataFrame
@st.cache
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data

# Function to make URLs clickable
def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'

# Streamlit app layout
def main():
    st.title("Streamlit App for Displaying Sitemap Data")

    # Load and cache the data
    csv_file = 'sitemap_data4_c4.csv'
    df = load_data(csv_file)

    # Make the URLs clickable
    df['URL'] = df.apply(lambda row: make_clickable(row['URL'], row['Article Title']), axis=1)
    
    # Display a search bar and filter data based on user input
    search_query = st.text_input("Search by Article Title:")
    if search_query:
        df = df[df['Article Title'].str.contains(search_query, case=False, na=False)]
    
    # Multi-select box for filtering by website
    website_options = df['Website Origin'].unique().tolist()
    websites_selected = st.multiselect("Filter by Website Origin:", options=website_options, default=website_options)
    df = df[df['Website Origin'].isin(websites_selected)]
    
    # Display the DataFrame
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
