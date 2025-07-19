import os
import argparse
from urllib.parse import urlparse

def create_folder_structure(urls):
    base_path = "data/downloadedsong"
    
    for url in urls:
        url = url.strip()
        if not url:
            continue
        
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) == 4:  # e.g., /charts/top-50/united-kingdom/belfast
            _, _, country, city = path_parts
            folder_path = os.path.join(base_path, "cities", country, city)
        elif len(path_parts) == 3:  # e.g., /charts/top-200/nigeria
            _, _, country = path_parts
            folder_path = os.path.join(base_path, "country", country)
        else:
            print(f"⚠️ Skipping invalid URL: {url}")
            continue
        
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created: {folder_path}")

def main():
    parser = argparse.ArgumentParser(description="Create folder structure from Shazam URLs.")
    parser.add_argument("url_file", help="Path to a text file containing Shazam URLs (one per line)")
    args = parser.parse_args()

    try:
        with open(args.url_file, "r") as f:
            urls = f.readlines()
        create_folder_structure(urls)
    except FileNotFoundError:
        print(f"❌ Error: File '{args.url_file}' not found.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
