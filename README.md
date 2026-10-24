# Cetacean Holiday

View a selection of holiday destinations ranked by nearby cetacean sightings, with some statistics.

If you're planning whale- and dolphin-watching for your next holiday, this is for you!

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

## Databases

| source | query | access | data wrangling |
|---|---|---|---|
|[GBIF](https://techdocs.gbif.org/en/openapi/)|sightings of cetaceans limited by year and polygon|free account|API requires a simplified polygon with at most a few hundred vertices|
|[Marine Regions]( https://www.marineregions.org/gazetteer.php?p=webservices&type=rest)|(multi)polygon by name|free|provides multi-polygon, which I converted to polygon

## License

Python code © Isaac Klinger  
Released under the [MIT](https://choosealicense.com/licenses/mit/)

[GBIF - Global Biodiversity Information Facility](https://techdocs.gbif.org/en/openapi/  
)  
Free and open access to biodiversity data  
Generally CC-BY-NC 4.0, some entries are under less strict licenses

[Marine Regions](https://www.marineregions.org/gazetteer.php?p=webservices&type=rest)  
A standard list of marine georeferenced place names and areas  
CC-BY 4.0