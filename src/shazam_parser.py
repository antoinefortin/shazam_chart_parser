import requests
from bs4 import BeautifulSoup
import os
import json
import argparse
from datetime import datetime
import sys
import csv

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def extract_location_info(url):
    parts = [p for p in url.split('/') if p]
    if 'top-200' in url:
        return 'country', parts[-1], None
    else:
        return 'city', parts[-2], parts[-1]

def scrape_shazam_chart(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        chart_data = []
        
        for item in soup.find_all('div', class_='page_songItem__lAdHy'):
            # Extract position
            position = item.find('span', class_='SongItem-module_rankingNumber__3oDWK')
            position = position.text.strip() if position else 'N/A'
            
            # BULLETPROOF TITLE EXTRACTION
            title = 'N/A'
            metadata_line = item.find('span', class_='SongItem-module_metadataLine__7Mm6B')
            if metadata_line:
                title_link = metadata_line.find('a', {'data-test-id': 'charts_userevent_list_songTitle'})
                if title_link:
                    title = title_link.text.strip()
            
            # Extract artist
            artist = item.find('a', {'data-test-id': 'charts_userevent_list_artistName'})
            artist = artist.text.strip() if artist else 'N/A'
            
            chart_data.append({
                'position': position,
                'title': title,
                'artist': artist
            })
            
        return chart_data
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def save_data(data, output_dir, filename, format_type):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{filename}.{format_type}")
    
    if format_type == 'json':
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format_type == 'csv':
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([f"# Chart Type: {data['chart_type']}"])
            writer.writerow([f"# Country: {data['country']}"])
            if data['city']:
                writer.writerow([f"# City: {data['city']}"])
            writer.writerow([f"# Date: {data['date']}"])
            writer.writerow([f"# URL: {data['url']}"])
            writer.writerow([])
            writer.writerow(['Position', 'Title', 'Artist'])
            for song in data['songs']:
                writer.writerow([song['position'], song['title'], song['artist']])
    
    else:  # txt format
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Chart Type: {data['chart_type']}\n")
            f.write(f"Country: {data['country']}\n")
            if data['city']:
                f.write(f"City: {data['city']}\n")
            f.write(f"Date: {data['date']}\n")
            f.write(f"URL: {data['url']}\n\n")
            f.write("Position\tTitle\tArtist\n")
            for song in data['songs']:
                f.write(f"{song['position']}\t{song['title']}\t{song['artist']}\n")
    
    print(f"Saved {format_type.upper()} data to {filepath}")

def process_urls(input_file, format_type='json'):
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        chart_type, country, city = extract_location_info(url)
        date_str = get_current_date()
        
        chart_data = scrape_shazam_chart(url)
        if not chart_data:
            continue
            
        result = {
            'chart_type': chart_type,
            'country': country,
            'city': city,
            'date': date_str,
            'url': url,
            'songs': chart_data
        }
        
        if chart_type == 'city':
            filename = f"{country}-{city}-{date_str}"
            output_dir = os.path.join('data', 'city')
        else:
            filename = f"{country}-{date_str}"
            output_dir = os.path.join('data', 'country')
        
        save_data(result, output_dir, filename, format_type)

def main():
    parser = argparse.ArgumentParser(description='Shazam Chart Scraper')
    parser.add_argument('input_file', help='Text file containing Shazam URLs')
    parser.add_argument('--format', choices=['json', 'txt', 'csv'], default='json',
                      help='Output format (default: json)')
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    process_urls(args.input_file, args.format)

if __name__ == "__main__":
    main()
