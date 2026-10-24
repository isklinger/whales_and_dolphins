import requests
import shapely
import os
from dotenv import load_dotenv
from pygbif import occurrences, species

"""
Conventions:

I've avoided hard-coding values obtained from the APIs,
even though this is a one-off project. This is so it's
clear where they're from and what they're for,
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
load_dotenv('../../gbif_credentials.env')

# Please specify an email address for Gazetteer requests
"""
GAZETEER_EMAIL = email
"""
load_dotenv('../../gazeteer_credentials.env')

# Fetch the British Exclusive Economic Zone polygon from Gazetteer
# https://www.marineregions.org/gazetteer.php?p=webservices&type=rest
gazeteer_record_name = 'British Exclusive Economic Zone'
gazeteer_mrgid = requests.get(
    'https://marineregions.org/rest/getGazetteerRecordsByNames.json/false/false/'
    + gazeteer_record_name
    + '/{name 2}/{name 3}/',
    headers = {'User-Agent': os.environ['GAZETEER_EMAIL']},
    timeout=30,
).json()[0][0]['MRGID']
# gazeteer_mrgid = '5696'

uk_eez_polygon = requests.get(
    'https://marineregions.org/rest/getGazetteerGeometries.jsonld/'
    + str(gazeteer_mrgid)
    + '/',
    headers = {'User-Agent': os.environ['GAZETEER_EMAIL']},
    timeout=30,
).json()['mr:hasGeometry'][0]['gsp:asWKT'][47:]

# GBIF requires polygons with 10,000 or fewer vertices
# Simplify EEZ polygon
vertex_limit = 10000
# Honestly, we don't need all the holes in the polygon.
# If there are Ceteceans on land, we definitely want to see them!
uk_eez_linearring = shapely.geometry.Polygon(
    shapely.from_wkt(uk_eez_polygon)).exterior
if shapely.get_num_points(uk_eez_linearring) > vertex_limit: # type: ignore
    coord_tolerance = [1*10**-5, 5*10**-5, 1*10**-4, 5*10**-4, 1*10**-3]
    # lattermost value of coord_tolerance gives highest acceptable tolerance (for me)
    while len(coord_tolerance) > 0:
        uk_eez_linearring = shapely.simplify(
            shapely.geometry.Polygon(
                shapely.from_wkt(uk_eez_polygon)).exterior,
                            tolerance=coord_tolerance.pop(0)
                        ) # type: ignore
        if shapely.get_num_points(uk_eez_linearring) <= vertex_limit: # type: ignore
            break
        if len(coord_tolerance) == 0:
            error_message='''Couldn't meet GBIF geometry vertex requirements.'''
            print(error_message)
            raise Exception(error_message)
uk_eez_polygon = shapely.to_wkt(shapely.geometry.Polygon(uk_eez_linearring))


# dict of species belonging to the infraorder Cetacea
# that are more commonly observed around the shores of Great Britain.
#
# species_dict is not currently being used anywhere;
# it's here for refactoring in case fetching all of Cetacea is too slow.
species_dict = {
    'Tursiops truncatus': 'common bottlenose dolphin',
    'Phocoena phocoena': 'harbour porpoise',
    'Balaenoptera physalus': 'fin whale',
    'Grampus griseus': '''Risso's dolphin''',
    'Delphinus delphis': 'short-beaked common dolphin',
    'Orcinus orca': 'orca',
    'Balaenoptera acutorostrata': 'common minke whale',
    'Physeter macrocephalus': 'sperm whale',
    'Lagenorhynchus albirostris': 'white-beaked dolphin',
    'Lagenorhynchus acutus': 'Atlantic white-sided dolphin',
    'Globicephala melas': 'long-finned pilot whale',
    'Megaptera novaeangliae': 'humpback whale',
    'Hyperoodon ampullatus': 'northern bottlenose whale',
}

species_list = [list(species_dict.keys())]

# Fetch taxonKey for 'Cetacea' from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/species.html
scientific_name = 'Cetacea'
taxon_rank = 'infraorder'
cetacea_taxon_key = str(
    species.name_backbone(scientificName=scientific_name, taxonRank=taxon_rank)[
        'usage'
    ]['key']
)
# cetacea_taxonKey = 'WP'

# Finally, what we're here for:
# Fetch occurences data set from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/occurrence.html

# strange format, passing positional arguments that look like explicit arguments  
occurrences.download('taxonKey = ' + str(cetacea_taxon_key),
                     'basisOfRecord = OCCURRENCE',
                     'geometry = ' + str(uk_eez_polygon),
                     'has_coordinate = True',
                     'has_geospatial_issue = False')

event_date = '2020,2025'
