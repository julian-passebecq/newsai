import streamlit as st
import pandas as pd

@st.experimental_memo
def load_data(csv_file):
    return pd.read_csv(csv_file)

def main():
    st.title("Sitemap Data Viewer")

    df = load_data('sitemap_data4_c4.csv')

    # Filter options
    year = st.selectbox('Select Year', options=df['Year'].unique())
    website_origin = st.multiselect('Select Website Origin', options=df['Website Origin'].unique())

    # Search bar
    search_query = st.text_input('Search by Article Title')

    # Applying filters
    filtered_df = df[df['Year'] == year] if year else df
    filtered_df = filtered_df[filtered_df['Website Origin'].isin(website_origin)] if website_origin else filtered_df
    filtered_df = filtered_df[filtered_df['Article Title'].str.contains(search_query, case=False)] if search_query else filtered_df

    st.dataframe(filtered_df, use_container_width=True)

if __name__ == "__main__":
    main()
