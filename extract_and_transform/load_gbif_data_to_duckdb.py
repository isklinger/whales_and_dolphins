import os
import zipfile
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

gbif_key_filename = 'gbif_download_key.txt'
with open(gbif_key_filename, 'r') as pgbif_key_file:
    pgbif_key = pgbif_key_file.read()

occurrences.download_get(pgbif_key)

with zipfile.ZipFile(pgbif_key + '.zip', 'r') as zip_ref:
    zip_ref.extractall('.')