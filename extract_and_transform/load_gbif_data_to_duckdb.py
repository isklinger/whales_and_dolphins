import os
import zipfile
import duckdb
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

if load_dotenv('../../gbif_credentials.env') is False:
    error_message='''Couldn't load GBIF credentials.'''
    print(error_message)
    raise Exception(error_message)

gbif_key_filename = '../data/raw/gbif_download_key.txt'
with open(gbif_key_filename, 'r') as pgbif_key_file:
    pgbif_key = pgbif_key_file.read()

occurrences.download_get(pgbif_key)

with zipfile.ZipFile(pgbif_key + '.zip', 'r') as zip_ref:
    zip_ref.extractall('.')

# Connect to 'gbif_cetaceans_great_britain.db'
duck = duckdb.connect('../data/raw/gbif_cetaceans_great_britain.db')
# (don't) describe the CSV table...
describe = duck.execute('''describe select * from read_csv(''' + """'""" + pgbif_key + '''.csv')''').fetchall()
#print(describe)

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
       year,
       dateIdentified
from read_csv(''' + """'""" + pgbif_key + '''.csv')
)

, right_table as (
select commonName, scientificName
from read_csv('../data/raw/species_dictionary.csv')
)

select left_table.*, right_table.commonName
from left_table
left join right_table
on left_table.species = right_table.scientificName
)
''')
duck.close()

print('''Data loaded! Take a look in the "load_and_model" path.''')