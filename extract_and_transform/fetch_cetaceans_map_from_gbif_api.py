import requests
import shapely
from dotenv import load_dotenv
from pygbif import occurrences, species

"""
Conventions:

I've avoided hard-coding values obtained from the APIs,
even though this is a one-off project,
so it's clear where they're from and what they're for,
and they don't appear as magic values out of nowhere.

Due to time constraints there are no try: except: blocks,
so none of this code fails gracefully.

python variables use_underscores
API parameters useCamelCase

Triple-double-quotes for comments
Triple-single-quotes for string-literals
"""

# Please register for a free account:
# Create an account for GBIF
# https://www.gbif.org/user/register
# and specify its credentials in an env file as follows:
"""
GBIF_USER = user
GBIF_PWD = password
GBIF_EMAIL = email
"""
load_dotenv("../../gbif_credentials.env")

# Fetch the British Exclusive Economic Zone polygon from Gazetteer
# https://www.marineregions.org/gazetteer.php?p=webservices&type=rest
gazeteer_record_name = "British Exclusive Economic Zone"
gazeteer_mrgid = requests.get(
    "https://marineregions.org/rest/getGazetteerRecordsByNames.json/false/false/"
    + gazeteer_record_name
    + "/{name 2}/{name 3}/",
    timeout=30,
).json()[0][0]["MRGID"]
# gazeteer_mrgid = '5696'

uk_eez_polygon = requests.get(
    "https://marineregions.org/rest/getGazetteerGeometries.jsonld/"
    + gazeteer_mrgid
    + "/",
    timeout=30,
).json()["mr:hasGeometry"][0]["gsp:asWKT"][47:]
# Imagine there's a block of code here that checks the number of vertices,
# instead of me manually counting field separators.
# 349,969 vertices... oof. GBIF accepts a maximum of 10,000
# Simplify EEZ polygon, less vertices and no holes
uk_eez_polygon = shapely.to_wkt(
                    shapely.geometry.Polygon(
                        shapely.simplify(
                            shapely.from_wkt(uk_eez_polygon),
                                             tolerance=0.005
                                        ).exterior.coords))
# Imagine we've verified the simplified polygon number of vertices is less-or-equal to 10000
# And honestly, we don't need all the holes in the polygon. If there are Ceteceans on land,
# we definitely want to see them!

# dict of species belonging to the infraorder Cetacea
# that are more commonly observed around the shores of Great Britain.
#
# species_dict is not currently being used anywhere;
# it's here for refactoring in case fetching all of Cetacea is too slow.
species_dict = {
    "Tursiops truncatus": "common bottlenose dolphin",
    "Phocoena phocoena": "harbour porpoise",
    "Balaenoptera physalus": "fin whale",
    "Grampus griseus": """Risso's dolphin""",
    "Delphinus delphis": "short-beaked common dolphin",
    "Orcinus orca": "orca",
    "Balaenoptera acutorostrata": "common minke whale",
    "Physeter macrocephalus": "sperm whale",
    "Lagenorhynchus albirostris": "white-beaked dolphin",
    "Lagenorhynchus acutus": "Atlantic white-sided dolphin",
    "Globicephala melas": "long-finned pilot whale",
    "Megaptera novaeangliae": "humpback whale",
    "Hyperoodon ampullatus": "northern bottlenose whale",
}

species_list = [list(species_dict.keys())]

# Fetch taxonKey for 'Cetacea' from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/species.html
scientific_name = "Cetacea"
taxon_rank = "infraorder"
cetacea_taxon_key = str(
    species.name_backbone(scientificName=scientific_name, taxonRank=taxon_rank)[
        "usage"
    ]["key"]
)
# cetacea_taxonKey = 'WP'

# Finally, what we're here for:
# Fetch occurences data set from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/occurrence.html
occurrences.download("taxonKey = " + cetacea_taxon_key)

event_date = "2020,2025"
occurrences.download("basisOfRecord = OCCURRENCE")
occurrences.download("geometry = " + uk_eez_polygon)
has_coordinate = True
has_geospatial_issue = False