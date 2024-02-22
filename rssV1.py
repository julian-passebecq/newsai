import csv
import feedparser

# Replace 'your_rss_feed_url_here' with the actual URL of the RSS feed
rss_url = 'https://data-mozart.com/feed/'
feed = feedparser.parse(rss_url)

# Specify the name of the CSV file where the data will be saved
csv_file_name = 'articles.csv'

# Open the CSV file in write mode
with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['Title', 'Published Date', 'Link'])
    
    # Loop through each entry in the feed and write the relevant data to the CSV file
    for entry in feed.entries:
        writer.writerow([entry.title, entry.published, entry.link])

print(f"CSV file '{csv_file_name}' created successfully.")
