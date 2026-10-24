import streamlit as st
import numpy as np
import pandas as pd
import duckdb

duck = duckdb.connect('../load_and_model/gbif_cetaceans_great_britain.db')

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)