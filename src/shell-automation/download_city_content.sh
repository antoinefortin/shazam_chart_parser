#!/bin/bash

# Configuration
JSON_DIR="$1"
BASE_DIR="data/downloadedsong/cities"
MAX_SONGS=5  # Number of songs to download per file

# Validate input
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/city_json/folder"
    exit 1
fi

if [ ! -d "$JSON_DIR" ]; then
    echo "Error: Directory '$JSON_DIR' not found"
    exit 1
fi

# Main processing function
process_city_json() {
    local json_file="$1"
    local country=$(jq -r '.country' "$json_file")
    local city=$(jq -r '.city' "$json_file")
    local filename=$(basename "$json_file" .json)
    local output_dir="$BASE_DIR/$country/$city"
    
    echo -e "\n# Processing: $city, $country ($filename.json)"
    echo "# Output directory: $output_dir"
    
    mkdir -p "$output_dir"
    
    # Generate and execute download commands
    jq -r --arg dir "$output_dir" \
        --arg max "$MAX_SONGS" \
        '.songs[0:($max|tonumber)][] | 
        "yt-dlp -x --audio-format mp3 --no-warnings \"ytsearch1:\(.artist) \(.title) official audio\" -o \"\($dir)/\(.position). \(.artist) - \(.title).%(ext)s\""' \
        "$json_file" | while read cmd; do
        
        echo "$cmd"
        if ! eval "$cmd"; then
            echo "Warning: Failed to download song"
        fi
    done
}

# Process all city JSON files
find "$JSON_DIR" -type f -name "*.json" | while read json_file; do
    process_city_json "$json_file"
done

echo -e "\nAll city downloads completed in $BASE_DIR/"
