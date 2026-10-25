import requests
import shapely
import os
from pathlib import Path
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

All the # type=ignore comments are for the linter
which fails to handle shapely types properly 
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
gbif_credentials  = Path(__file__).parent.parent.parent / 'gbif_credentials.env'
if load_dotenv(gbif_credentials) is False:
    error_message='''Couldn't load GBIF credentials.'''
    print(error_message)
    raise Exception(error_message)

# Please specify an email address for Gazetteer requests
"""
GAZETEER_EMAIL = email
"""
gazeteer_credentials  = Path(__file__).parent.parent.parent / 'gazeteer_credentials.env'
if load_dotenv(gazeteer_credentials) is False:
    error_message='''Couldn't load Gazeteer credentials.'''
    print(error_message)
    raise Exception(error_message)

# Check if there's a local copy of the polygon data, otherwise request and save data
polygon_filename = Path(__file__).parent.parent / 'data/raw/great_britain_polygon.wkt'
if os.path.isfile(polygon_filename) and os.access(polygon_filename, os.R_OK):
    with open(polygon_filename, 'r') as polygon_file:
        gb_polygon = polygon_file.read()
else:
    # Fetch the Great Britain polygon from Gazetteer
    # https://www.marineregions.org/gazetteer.php?p=webservices&type=rest
    gazeteer_record_name = 'Great Britain'
    gazeteer_mrgid = requests.get(
        'https://marineregions.org/rest/getGazetteerRecordsByNames.json/false/false/'
        + gazeteer_record_name
        + '/{name 2}/{name 3}/',
        headers = {'User-Agent': os.environ['GAZETEER_EMAIL']},
        timeout=30,
    ).json()[0][0]['MRGID']
    # gazeteer_mrgid = '47642'

    gb_polygon = requests.get(
        'https://marineregions.org/rest/getGazetteerGeometries.jsonld/'
        + str(gazeteer_mrgid)
        + '/',
        headers = {'User-Agent': os.environ['GAZETEER_EMAIL']},
        timeout=30,
    ).json()['mr:hasGeometry'][0]['gsp:asWKT'][47:]
    # It's a multi-polygon, so we'll select
    # the polygon with the largest area, Great Britain
    just_great_britain = max(shapely.from_wkt(gb_polygon).geoms, key=lambda a: a.area)
    gb_polygon = shapely.to_wkt(
                    shapely.orient_polygons(
                        shapely.geometry.Polygon(just_great_britain)))
    with open(polygon_filename, 'w') as polygon_file:
         polygon_file.write(gb_polygon)


# Buffer GB polygon out into the seas by 0.8 of a degree
gb_polygon_buffer = shapely.buffer(
                        shapely.geometry.Polygon(
                            shapely.from_wkt(gb_polygon)).exterior, # type: ignore
                         0.8)
gb_polygon = shapely.to_wkt(
                shapely.union(shapely.geometry.Polygon(shapely.from_wkt(gb_polygon)), # type: ignore
                   gb_polygon_buffer))

# I find GBIF requires polygons with around 200 or fewer vertices
# Simplify GB polygon
vertex_limit = 200

gb_linear_ring = shapely.geometry.Polygon(
    shapely.from_wkt(gb_polygon)).exterior # type: ignore

if shapely.get_num_points(gb_linear_ring) > vertex_limit: # type: ignore
    coord_tolerance = [1*10**-4, 1*10**-3, 1*10**-2, 1*10**-1]
    # lattermost value of coord_tolerance gives highest acceptable tolerance (for me)
    while len(coord_tolerance) > 0:
        gb_linear_ring = shapely.simplify(
            shapely.geometry.Polygon(
                shapely.from_wkt(gb_polygon)).exterior, # type: ignore
                            tolerance=coord_tolerance.pop(0)
                        )
        if shapely.get_num_points(gb_linear_ring) <= vertex_limit: # type: ignore
            break
        if len(coord_tolerance) == 0:
            error_message='''Couldn't meet GBIF geometry vertex requirements.'''
            print(error_message)
            raise Exception(error_message)

# GBIF requires polygon with counter-clockwise exterior ring
gb_polygon = shapely.to_wkt(
                    shapely.orient_polygons(
                        shapely.geometry.Polygon(gb_linear_ring)))

# Fetch taxonKey for 'Cetacea' from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/species.html
scientific_name = 'Cetacea'
taxon_rank = 'infraorder'
cetacea_taxon_key = str(
    species.name_backbone(scientificName=scientific_name, taxonRank=taxon_rank)[
        'usage'
    ]['key'])
# cetacea_taxon_key = 'WP'

# Finally, what we're here for:
# Query occurence data from GBIF
# https://pygbif.readthedocs.io/en/latest/modules/occurrence.html
gbif_download_info = occurrences.download(['taxonKey = ' + str(cetacea_taxon_key),
                                           'geometry = ' + str(gb_polygon),
                                           'hasCoordinate = True',
                                           'hasGeospatialIssue = False',
                                           'year = 2020,2025'])

if gbif_download_info[0][0:2] == '00':
    # very unreliable way to check whether the download key has been retrieved
    gbif_key_filename = Path(__file__).parent  / 'data/raw/gbif_download_key.txt'
    with open(gbif_key_filename, 'w') as pgbif_key_file:
         pgbif_key_file.write(gbif_download_info[0])
    print('''
GBIF download key: ''' + gbif_download_info[0] + '''
Your download key has been recorded in "''' + gbif_key_filename + '''" and
you will receive an email from GBIF when your download is available.
Run "load_gbif_data_to_duckdb.py" when it's available to load it into the database.
''')
else:
    print('''Failed to retrieve download key.''')