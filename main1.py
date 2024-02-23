import streamlit as st
import pandas as pd

# Updated function to load data using Streamlit's new caching command
@st.experimental_memo
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data

def main():
    st.title("Streamlit App for Displaying Sitemap Data")

    # Path to the CSV file
    csv_file = 'sitemap_data_cleaned.csv'
    
    # Load the data
    df = load_data(csv_file)

    # Display a search bar and filter data based on user input
    search_query = st.text_input("Search by Article Title:")
    if search_query:
        df = df[df['Article Title'].str.contains(search_query, case=False, na=False)]
    
    # Multi-select box for filtering by website origin
    websites = df['Website Origin'].unique().tolist()
    selected_websites = st.multiselect("Filter by Website Origin:", websites, default=websites)
    df_filtered = df[df['Website Origin'].isin(selected_websites)]

    # Make URLs clickable
    def make_clickable(name, link):
        return f'<a target="_blank" href="{link}">{name}</a>'

    df_filtered['clickable_urls'] = df_filtered.apply(lambda x: make_clickable(x['Article Title'], x['URL']), axis=1)

    # Convert DataFrame to HTML for clickable links and display using st.markdown
    st.markdown(df_filtered.to_html(escape=False, columns=['Last Modified', 'Website Origin', 'Year', 'clickable_urls'], index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
