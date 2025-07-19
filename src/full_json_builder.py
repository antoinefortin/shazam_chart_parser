import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import sys

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def extract_location_info(url):
    parts = [p for p in url.split('/') if p]
    if 'top-200' in url:
        return {'chart_type': 'country', 'country': parts[-1], 'city': None}
    else:
        return {'chart_type': 'city', 'country': parts[-2], 'city': parts[-1]}

def scrape_shazam_chart(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = []
        
        for item in soup.find_all('div', class_='page_songItem__lAdHy'):
            # Extract position
            position = item.find('span', class_='SongItem-module_rankingNumber__3oDWK')
            position = position.text.strip() if position else 'N/A'
            
            # Extract title
            title = 'N/A'
            metadata_line = item.find('span', class_='SongItem-module_metadataLine__7Mm6B')
            if metadata_line:
                title_link = metadata_line.find('a', {'data-test-id': 'charts_userevent_list_songTitle'})
                if title_link:
                    title = title_link.text.strip()
            
            # Extract artist
            artist = item.find('a', {'data-test-id': 'charts_userevent_list_artistName'})
            artist = artist.text.strip() if artist else 'N/A'
            
            songs.append({
                'position': position,
                'title': title,
                'artist': artist
            })
            
        return songs
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def generate_complete_json(input_file):
    complete_data = {
        'metadata': {
            'generated_at': get_current_date(),
            'source_file': input_file,
            'total_charts': 0
        },
        'charts': []
    }
    
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        location = extract_location_info(url)
        chart_data = scrape_shazam_chart(url)
        
        if chart_data:
            chart_entry = {
                'url': url,
                'type': location['chart_type'],
                'country': location['country'],
                'city': location['city'],
                'date_scraped': get_current_date(),
                'songs': chart_data
            }
            complete_data['charts'].append(chart_entry)
    
    complete_data['metadata']['total_charts'] = len(complete_data['charts'])
    
    # Save the complete JSON
    output_file = f"shazam_complete_data_{get_current_date()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nComplete JSON data saved to {output_file}")
    print(f"Total charts processed: {len(complete_data['charts'])}")
    print(f"Contains: {sum(len(chart['songs']) for chart in complete_data['charts'])} songs")

def main():
    if len(sys.argv) != 2:
        print("Usage: python shazam_processor.py <input_file.txt>")
        print("Example: python shazam_processor.py urls.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    generate_complete_json(input_file)

if __name__ == "__main__":
    main()
