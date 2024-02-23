import streamlit as st
import pandas as pd

@st.experimental_memo
def load_data(csv_file):
    return pd.read_csv(csv_file)

def main():
    st.title("Sitemap Data Viewer")

    df = load_data('sitemap_data4_c4.csv')

    # Multi-select filters for year and website origin
    selected_years = st.multiselect('Select Year(s)', options=df['Year'].unique())
    selected_origins = st.multiselect('Select Website Origin(s)', options=df['Website Origin'].unique())

    # Filter the DataFrame based on selections
    if selected_years:
        df = df[df['Year'].isin(selected_years)]
    if selected_origins:
        df = df[df['Website Origin'].isin(selected_origins)]

    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
