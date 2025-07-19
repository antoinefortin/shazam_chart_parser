import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import sys

def get_current_date():
    """Return current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def extract_location_info(url):
    """Extract country and city from URL"""
    parts = url.split('/')
    country = parts[-2]
    city = parts[-1]
    return country, city

def scrape_city_chart(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = []
        
        for item in soup.find_all('div', class_='page_songItem__lAdHy'):
            # Extract rank
            rank = item.find('span', class_='SongItem-module_rankingNumber__3oDWK').text.strip()
            
            # Extract title
            title_element = item.find('span', class_='SongItem-module_metadataLine__7Mm6B').find('a', {'data-test-id': 'charts_userevent_list_songTitle'})
            title = title_element.text.strip() if title_element else 'N/A'
            
            # Extract artist
            artist_element = item.find('a', {'data-test-id': 'charts_userevent_list_artistName'})
            artist = artist_element.text.strip() if artist_element else 'N/A'
            
            songs.append(f"{rank}\t{title}\t{artist}")
            
        return songs
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def process_urls(input_file):
    # Create output directory if it doesn't exist
    os.makedirs('city', exist_ok=True)
    
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        country, city = extract_location_info(url)
        date_str = get_current_date()
        output_file = f"city/{country}-{city}-{date_str}.txt"
        
        songs = scrape_city_chart(url)
        if songs:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Position\tTitle\tArtist\n")
                f.write("\n".join(songs))
            print(f"Saved {len(songs)} songs to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python shazam_cities.py <input_file.txt>")
        print("Example: python shazam_cities.py city_urls.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    process_urls(input_file)
