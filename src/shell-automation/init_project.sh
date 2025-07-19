rm -R data


python3.11 shazam_parser.py ressource/countrylist.txt --format csv
python3.11 shazam_parser.py ressource/countrylist.txt --format text
python3.11 shazam_parser.py ressource/countrylist.txt --format json

python3.11 shazam_parser.py ressource/citylist.txt --format csv
python3.11 shazam_parser.py ressource/citylist.txt --format text
python3.11 shazam_parser.py ressource/citylist.txt --format json
