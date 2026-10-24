# Cetacean Holiday

View a selection of holiday destinations ranked by nearby cetacean sightings, with some statistics.

## Who is it for

Would-be holidaymakers planning whale- and dolphin-watching for their next holiday.

## Usage

Tested in Python 3.14  
Requires a free [GBIF](https://www.gbif.org/) account.


```bash
git clone https://github.com/isklinger/whales_and_dolphins

cd whales_and_dolphins
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp gazeteer_credentials.env.example ../gazeteer_credentials.env
# ...and update gazeteer_credentials.env with your credentials
cp gbif_credentials.env.example ../gbif_credentials.env
# ...and update gbif_credentials.env with your credentials

cd extract_and_transform
python3 fetch_cetaceans_map_from_gbif_api.py
# you will be prompted to wait until you receive an email from GBIF saying the download is ready
python3 load_gbif_data_to_duckdb.py
streamlit run app/app.py
```

## License

Python code © Isaac Klinger  
Released under the [MIT](https://choosealicense.com/licenses/mit/)

GBIF - Global Biodiversity Information Facility  
Free and open access to biodiversity data  
https://techdocs.gbif.org/en/openapi/  
Generally CC-BY-NC 4.0, some entries are under less strict licenses

Marine Regions - a standard list of marine georeferenced place names and areas  
https://www.marineregions.org/gazetteer.php?p=webservices&type=rest  
CC-BY 4.0