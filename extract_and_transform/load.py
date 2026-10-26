import zipfile
import duckdb
from pathlib import Path
from dotenv import load_dotenv
from pygbif import occurrences

"""
Conventions:

Due to time constraints there are no try: except: blocks,
so none of this code fails gracefully.

python variables use_underscores
API parameters useCamelCase

Triple-double-quotes for comments
Triple-single-quotes for string-literals
"""

gbif_credentials  = Path(__file__).parent.parent.parent / 'gbif_credentials.env'
if load_dotenv(gbif_credentials) is False:
    error_message='''Couldn't load GBIF credentials.'''
    print(error_message)
    raise Exception(error_message)

gbif_key_filename = Path(__file__).parent.parent / 'data/raw/gbif_download_key.txt'
with open(gbif_key_filename, 'r') as pgbif_key_file:
    pgbif_key = pgbif_key_file.read()

data_raw_str = str(Path(__file__).parent.parent / 'data/raw') + '/'
occurrences.download_get(pgbif_key, data_raw_str)

download_file_path_str = data_raw_str + str(pgbif_key) + '.zip'
with zipfile.ZipFile(download_file_path_str, 'r') as zip_ref:
    zip_ref.extractall(data_raw_str)

# Connect to 'gbif_cetaceans_great_britain.db'
db_filename = Path(__file__).parent.parent / 'data/marts/gbif_cetaceans_great_britain.db'
duck = duckdb.connect(db_filename)
# (don't) describe the CSV table...
describe = duck.execute('''describe select * from read_csv(''' +
                        """'""" + data_raw_str + 
                        pgbif_key + '''.csv')''').fetchall()
#print(describe)

species_dictionary_filename = Path(__file__).parent.parent / 'data/marts/species_dictionary.csv'

# create a table, select some columns from the CSV, put the selected columns in the table
duck.execute('''
drop table if exists cetaceans_gb;
create table cetaceans_gb as
(
with
left_table as (
select gbifID,
       species,
       locality,
       stateProvince,
       individualCount,
       decimalLatitude as latitude,
       decimalLongitude as longitude,
       eventDate as date,
       day,
       month,
       year
from read_csv(''' + """'""" + data_raw_str + pgbif_key + '''.csv')
)

, right_table as (
select commonName, scientificName
from read_csv(''' + """'""" + str(species_dictionary_filename) + """'""" + ''')
)

select left_table.*, right_table.commonName
from left_table
left join right_table
on left_table.species = right_table.scientificName
)
''')
duck.close()

print('''
Data loaded! Run the app with:

streamlit run app/streamlit.py
''')
