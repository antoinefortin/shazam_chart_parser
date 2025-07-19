import requests
import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

def extract_country_name(url):
    """Extract country name from URL"""
    parsed = urlparse(url)
    path = parsed.path
    # Extract the last part of the path (country name)
    country = path.split('/')[-1]
    return country if country != 'world' else 'global'

def scrape_shazam_chart(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        chart_list = soup.find('div', class_='ListShowMoreLess_container__t4TNB page_chartList__aBclW')
        
        if not chart_list:
            print(f"Could not find chart list container for {url}")
            return None
            
        song_items = chart_list.find_all('li')
        songs_data = []
        
        for item in song_items:
            # Extract song title
            title_element = item.find('span', class_='SongItem-module_metadataLine__7Mm6B')
            if title_element:
                title_element = title_element.find('a', {'data-test-id': 'charts_userevent_list_songTitle'})
            title = title_element.text if title_element else 'N/A'
            
            # Extract artist name
            artist_element = item.find('a', {'data-test-id': 'charts_userevent_list_artistName'})
            artist = artist_element.text if artist_element else 'N/A'
            
            songs_data.append(f"{title.strip()} - {artist.strip()}")
        
        return songs_data
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def process_urls(input_file):
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        country = extract_country_name(url)
        output_dir = "data/" + country
        output_file = f"{country}-data.txt"
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        songs = scrape_shazam_chart(url)
        if songs:
            file_path = os.path.join(output_dir, output_file)
            with open(file_path, 'w', encoding='utf-8') as f:
                for idx, song in enumerate(songs, start=1):
                    f.write(f"{idx}. {song}\n")
            print(f"Successfully saved {len(songs)} songs to {file_path}")
        
        # Be polite with a delay between requests
        time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python shazam_scraper.py <input_file.txt>")
        print("Example: python shazam_scraper.py country_urls.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    process_urls(input_file)
