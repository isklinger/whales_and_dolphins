from __future__ import annotations

from pathlib import Path

import duckdb
import folium
import folium.features
import geopandas as gpd
import pandas as pd
import requests
import shapely
import streamlit as st

from streamlit_folium import st_folium

st.set_page_config(
    page_title="Whales and dolphins: extract, load, transform",
    page_icon="🫍",
    layout="wide",
)


p = Path(__file__).parent.parent / "data/raw/states.csv"
USA_DATA = pd.read_csv(p)


@st.cache_resource
def duck():
    duck = duckdb.connect('../data/raw/gbif_cetaceans_great_britain.db')
    duck.sql("install spatial")
    duck.sql("load spatial")

    return duck

def duck_circle(latitude, longitude):
    """Return a circle around provided coordinates"""
    # query duckdb from python
    #https://github.com/duckdb/duckdb-blog-examples/blob/main/duckdb_streamlit/utils.py

    # spatial join by distance
    #ST_DWithin(a, b, x)

    # inscribing a circle
    #https://duckdb.org/docs/2.0/core_extensions/spatial/functions#st_buffer
    #GEOMETRY ST_Buffer (geom GEOMETRY, distance DOUBLE, num_triangles INTEGER)

    pass

def new_marker():
    pass

@st.cache_data
def _get_all_state_bounds() -> dict:
    url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    return requests.get(url).json()


@st.cache_data
def get_state_bounds(state: str) -> dict:
    data = _get_all_state_bounds()
    state_entry = next(f for f in data["features"] if f["properties"]["name"] == state)
    return {"type": "FeatureCollection", "features": [state_entry]}


def get_state_from_lat_lon(lat: float, lon: float) -> str:
    state_row = USA_DATA[
        USA_DATA.latitude.between(lat - 0.0001, lat + 0.0001)
        & USA_DATA.longitude.between(lon - 0.0001, lon + 0.0001)
    ].iloc[0]
    return state_row["state"]


def get_population(state: str) -> int:
    return USA_DATA.set_index("state").loc[state]["population"]


def main():
    duckdb_conn = duck()

    if "last_object_clicked" not in st.session_state:
        st.session_state["last_object_clicked"] = None
    if "selected_state" not in st.session_state:
        st.session_state["selected_state"] = "Indiana"

    bounds = get_state_bounds(st.session_state["selected_state"])

    st.write(f"## {st.session_state['selected_state']}")
    population = get_population(st.session_state["selected_state"])
    st.write(f"### Population: {population:,}")

    center = None
    if st.session_state["last_object_clicked"]:
        center = st.session_state["last_object_clicked"]

    m = folium.Map(location=[51.51305718496589+4,
                            -0.09419110869791583-5],
                zoom_start=5)

    # If you want to dynamically add or remove items from the map,
    # add them to a FeatureGroup and pass it to st_folium
    fg = folium.FeatureGroup(name="State bounds")
    fg.add_child(folium.features.GeoJson(bounds))

    capitals = USA_DATA

    for capital in capitals.itertuples():
        fg.add_child(
            folium.Marker(
                location=[capital.latitude, capital.longitude],
                popup=f"{capital.capital}, {capital.state}",
                tooltip=f"{capital.capital}, {capital.state}",
                icon=folium.Icon(color="green")
                if capital.state == st.session_state["selected_state"]
                else None,
            )
        )

    out = st_folium(
        m,
        feature_group_to_add=fg,
        center=center,
        width=500,
        height=500,
    )

    if (
        out["last_object_clicked"]
        and out["last_object_clicked"] != st.session_state["last_object_clicked"]
    ):
        st.session_state["last_object_clicked"] = out["last_object_clicked"]
        state = get_state_from_lat_lon(*out["last_object_clicked"].values())
        st.session_state["selected_state"] = state
        st.rerun()

if __name__ == "__main__":
    main()

comment="""
TODO

Species selection checkboxes

Highlight sightings within radius

Probability of sighting a species within radius in a given month:
sum(distinct(sightings_by_days_of_month))/length_days(month)

Map with hover tooltip that shows species, date, etc
"""