## Cetacean Holiday (What I built and who for)

View arbitrary coordinates with nearby cetacean sightings statistics.

If you're planning whale- and dolphin-watching for your next holiday, this is for you!

## Usage (How to run it)

Tested in Python 3.14  
Requires a free [GBIF](https://www.gbif.org/) account.

```bash
# clone
git clone https://github.com/isklinger/whales_and_dolphins

# set up python virtual environment
cd whales_and_dolphins
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# set up credentials
cp gazeteer_credentials.env.example ../gazeteer_credentials.env
# gazeteer - email optional
cp gbif_credentials.env.example ../gbif_credentials.env
# gbif - requires username, password, and email

# extract, transform, load
python3 extract_and_transform/query_api.py
# you will be prompted to wait until you receive an email from GBIF saying the download is ready
python3 extract_and_transform/load.py

# run the app
streamlit run app/streamlit.py
```

## Databases (How it works)

| source | query | credentials requirements | data shaping |
|:-:|---|:-:|---|
|[GBIF](https://techdocs.gbif.org/en/openapi/)|sightings of cetaceans limited by year and polygon|free account|the query provides many columns that aren't used by the marts, so I didn't select them when loading into the local database|
|[Marine Regions]( https://www.marineregions.org/gazetteer.php?p=webservices&type=rest)|(multi-)polygon by name|none|the query provides a multi-polygon, which I converted to a polygon and supplemented with a buffer|

### Freshness and updates

For portability, and so I can have near certainty that the app displays the same results everywhere, the GBIF query selects the years 2020 through 2025 each time. If up-to-date data is required, the query can be optimised in a straightforward way: query for the latest date in the local database, then query GBIF for data from that day onward. If no data is found locally, query GBIF for data from five years ago onward.

The Marine Regions database is queried for the geospatial polygon of the island of Great Britain. This information can be considered immutable within this project's scope and level of precision, and so if a file with the polygon data already locally exists, the local data is used. There are no freshness checks, although these can be implemented by recording the date of the most recent remote query. The polygon may be updated annualy, in case of changes in the island's coastline.

## Data shaping (How it works)

### Extracting and loading:

#### GBIF
- The data from GBIF is generally complete and consistent. 
- I preselected, using the query from the GBIF database, rows without geospatial issues.
- There are clear data sampling artifacts like coordinates arranged neatly along a radius, but this spatial (in)accuracy is sufficiently small for general whale-watching purposes in open seas.

#### Marine Regions

- The data from Marine Regions is, for the purposes of this project, completely accurate and correct, or the "ground truth".
- I simplified the polygons returned by the database since they are too detailed to be used with the GBIF API. 

### Transforming:

- The Streamlit app queries DuckDB with a coordinate pair generated when the user last clicks on the map.
- DuckDB returns GBIF data within the specified radius from the coordinates, which is displayed on the app.
- The app displays the probability of sighting cetaceans in the specified month within the given radius, by the number of distinct days with sightings of one or more cetaceans.

## Possible enhancements (What I would do next)

- See [freshness and updates section](#freshness-and-updates)
- List popular destinations and sort them by count of nearby sightings.
- List nearest popular destination when selecting a coordinate.
- Filter sightings by species.
- Tooltips for sighting instances.
- Include species outside cetaceans, specifically popular birds and national park wildlife.
- Filter species by activity: birdwatching, boat tour, hiking.
- Provide data about local related business and national parks.

## How this was made

I coded this in Visual Studio Code and vim. Python environment set up in [a custom Ubuntu container](https://github.com/isklinger/container-image-systemd-ubuntu-xrdp). The Streamlit Folium tutorial by Randy Zwitch was used extensively as I have never used Streamlit or Folium before.

### Use of AI (Where AI helped)

No AI was used in the making of this project.

## Licenses

Tutorials © Stichting DuckDB Foundation  
Released under the [MIT](https://choosealicense.com/licenses/mit/) license

Tutorials © Randy Zwitch, creator of Streamlit Folium  
Released under the MIT license

All other code © Isaac Klinger  
Released under the MIT license

[GBIF - Global Biodiversity Information Facility](https://techdocs.gbif.org/en/openapi/  
)  
Free and open access to biodiversity data  
Most entries released under the CC-BY-NC 4.0 license, some entries are under less strict licenses

[Marine Regions](https://www.marineregions.org/gazetteer.php?p=webservices&type=rest)  
A standard list of marine georeferenced place names and areas  
Released under the CC-BY 4.0 license

## About me

Hi, I'm Isaac. I moved to London in early 2025, where I'm living with my wonderful wife who grew up in London.

I've been using python for personal projects for many years. After attending a meetup at The Data School in mid-2026, I delved deeper into dbt and data analysis. I enjoy the modular and structured source-model-test design concept of dbt. Its clean design reminds me of the concepts behind python's syntax. I enjoy the visual and technical aspects of data analysis.

I'm employed as a datacenter system adminstrator for a company based in Soho, keeping installations of Debian, Nginx, Apache, MariaDB, and the sort humming along.