# Cetacean Holiday

View a selection of holiday destinations ranked by nearby cetacean sightings, with some statistics.

If you're planning whale- and dolphin-watching for your next holiday, this is for you!

## Usage

Tested in Python 3.14  
Requires a free [GBIF](https://www.gbif.org/) account.


```bash
git clone https://github.com/isklinger/whales_and_dolphins

cd whales_and_dolphins
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

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

| source | query | credentials requirements | data shaping |
|:-:|---|:-:|---|
|[GBIF](https://techdocs.gbif.org/en/openapi/)|sightings of cetaceans limited by year and polygon|free account|the query provides many columns that aren't used by the marts, so I didn't select them when loading into the local database|
|[Marine Regions]( https://www.marineregions.org/gazetteer.php?p=webservices&type=rest)|(multi-)polygon by name|none|the query provides a multi-polygon, which I converted to a polygon and supplemented with a buffer|

## Data shaping

The data from GBIF is generally complete and correct. Very few values have user-submitted info in the wrong field which can be detected by selecting distinct values and looking for outliers.

The data from Marine Regions is accurate and correct, but the polygons have to be simplified locally since they are too detailed to be used with the GBIF API. 


## Possible enhancements

- More species, specifically popular birds and national park wildlife. Categorise views by activity: birdwatching, boat tour, hiking.
- Data about local related business and national parks
- Use custom tiles that include more interesting and pertinent information in the tile layer itself: [Dynamic Tile Service](https://github.com/federicotallis/Duckdb_Dynamic_Tile_Service/blob/main/Streamlit/app.py)

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

## About me

Hi, I'm Isaac. I moved to London in early 2025, where I'm living with my wonderful wife who grew up in London.

I've been using python for personal projects for many years. After attending a meetup at The Data School in mid-2026, I delved deeper into dbt and data analysis. I enjoy the modular and structured source-model-test design concept of dbt. Its clean design reminds me of the concepts behind python's syntax. I enjoy the visual and technical aspects of data analysis.

I'm employed as a datacenter system adminstrator for a company based in Soho, keeping installations of Debian, Nginx, Apache, MariaDB, and the sort humming along.