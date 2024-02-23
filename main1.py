# ... [existing code]

def main():
    st.title('Article Search Across Multiple Websites')
    
    all_articles = []
    for website_name, sitemap_url in sitemap_urls.items():
        articles = parse_sitemap(sitemap_url)
        for article in articles:
            article['Website'] = website_name  # Add website name to each article
        all_articles.extend(articles)
    
    # Check if there are articles before proceeding
    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        
        # Check if 'Last Modified' column exists before trying to convert it
        if 'Last Modified' in articles_df.columns:
            articles_df['Last Modified'] = pd.to_datetime(articles_df['Last Modified'], errors='coerce', utc=True)
        
        search_query = st.text_input('Enter search term:')
        if search_query:
            filtered_articles = articles_df[articles_df['URL'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_articles = articles_df

        st.write(filtered_articles)
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    main()
