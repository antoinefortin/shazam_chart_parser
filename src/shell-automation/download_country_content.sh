#!/bin/bash

# Check if directory is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/json/folder"
    exit 1
fi

json_dir="$1"
base_dir="data/downloadedsong/countries"

# Verify directory exists
if [ ! -d "$json_dir" ]; then
    echo "Error: Directory '$json_dir' not found"
    exit 1
fi

# Process each JSON file
find "$json_dir" -type f -name "*.json" | while read json_file; do
    # Extract country and filename without extension
    country=$(jq -r '.country' "$json_file")
    filename=$(basename "$json_file" .json)
    
    # Create output directory
    output_dir="$base_dir/$country/$filename"
    mkdir -p "$output_dir"
    
    echo ""
    echo "# Processing: $filename.json"
    echo "# Output directory: $output_dir"
    echo ""

    # Generate and execute commands for first 5 songs
    jq -r --arg dir "$output_dir" '.songs[0:5][] | 
    "yt-dlp -x --audio-format mp3 --ffmpeg-location \"$(command -v ffmpeg)\" \"ytsearch1:\(.artist) \(.title) official audio\" -o \"\($dir)/\(.artist) - \(.title).%(ext)s\""' "$json_file" | 
    while read cmd; do
        echo "$cmd"
        eval "$cmd"
    done
done

echo ""
echo "All downloads completed in $base_dir/"
