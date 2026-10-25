import duckdb
import folium
import folium.features
import streamlit as st
from pathlib import Path
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Whales and dolphins: extract, load, transform",
    page_icon="🫍",
    layout="wide",
)


species_dict_csv_path = Path(__file__).parent.parent / "data/raw/species_dictionary.csv"
if species_dict_csv_path.exists():
    with species_dict_csv_path.open() as species_dict_csv_file:
        species_dictionary = species_dict_csv_file.read()


@st.cache_resource
def duck():
    duck = duckdb.connect('../data/raw/gbif_cetaceans_great_britain.db')
    duck.sql("install spatial")
    duck.sql("load spatial")

    return duck

def duck_circle(coordinates_dict):
    """Return a circle around provided coordinates"""
    # query duckdb from python
    #https://github.com/duckdb/duckdb-blog-examples/blob/main/duckdb_streamlit/utils.py

    # spatial join by distance
    #ST_DWithin(a, b, x)

    # inscribing a circle
    #https://duckdb.org/docs/2.0/core_extensions/spatial/functions#st_buffer
    #GEOMETRY ST_Buffer (geom GEOMETRY, distance DOUBLE, num_triangles INTEGER)
    return '''
    { "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": { "layer": "Drawn Shapes", "isBuffer": false }, "geometry": { "type": "Point", "coordinates": [ -1.4941406250000002, 53.09754162819622 ] } }, { "type": "Feature", "properties": { "layer": "Drawn Shapes_buffer_20km", "isBuffer": true }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -1.1945958403290746, 53.0971656535093 ], [ -1.2001115981138688, 53.13226935224857 ], [ -1.216953500782286, 53.166051103155084 ], [ -1.2444977087390368, 53.19720810648272 ], [ -1.2817015061883494, 53.224536083457494 ], [ -1.327140903852712, 53.246976609763536 ], [ -1.3790644320172967, 53.26365904940491 ], [ -1.4354612179172208, 53.27393528342674 ], [ -1.4941406250000002, 53.27740570094113 ], [ -1.5528200320827796, 53.27393528342674 ], [ -1.609216817982704, 53.26365904940491 ], [ -1.6611403461472884, 53.246976609763536 ], [ -1.7065797438116512, 53.224536083457494 ], [ -1.743783541260964, 53.19720810648272 ], [ -1.7713277492177146, 53.166051103155084 ], [ -1.7881696518861319, 53.13226935224857 ], [ -1.7936854096709263, 53.0971656535093 ], [ -1.7876904239686002, 53.06209057333404 ], [ -1.7704422471882388, 53.02839032155156 ], [ -1.7426265686942706, 52.99735529124763 ], [ -1.7053274349920995, 52.97017119275154 ], [ -1.6599833537402233, 52.94787454653408 ], [ -1.6083312878947051, 52.931314083803 ], [ -1.5523407843248762, 52.921119352791806 ], [ -1.4941406250000002, 52.91767755545131 ], [ -1.4359404656751245, 52.921119352791806 ], [ -1.3799499621052957, 52.931314083803 ], [ -1.3282978962597773, 52.94787454653408 ], [ -1.2829538150079012, 52.97017119275154 ], [ -1.24565468130573, 52.99735529124763 ], [ -1.217839002811762, 53.02839032155156 ], [ -1.2005908260314004, 53.06209057333404 ], [ -1.1945958403290746, 53.0971656535093 ] ] ] } } ]}
    '''

def main():

    duckdb_conn = duck()
    
    # https://docs.streamlit.io/develop/concepts/architecture/session-state#initialization
    if "center" not in st.session_state:
        st.session_state["center"] = (51.51305718496589+4, -0.09419110869791583-5)
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = 6
    if "markers" not in st.session_state:
        st.session_state["markers"] = []
    if 'last_clicked' not in st.session_state:
        st.session_state['last_clicked'] = {'lat': st.session_state["center"][0],
                                            'lng': st.session_state["center"][1]}
    

    m = folium.Map(location=(51.51305718496589+4,
                             -0.09419110869791583-5),
                    zoom_start=4)

    # FeatureGroup
    fg = folium.FeatureGroup(name='radius')

    bounds = duck_circle(st.session_state['last_clicked'])
    fg.add_child(folium.features.GeoJson(bounds))

    marker = folium.Marker(
        location=[st.session_state['last_clicked']['lat'],
                    st.session_state['last_clicked']['lng']],
        popup='Something',
        tooltip=f"{st.session_state["last_clicked"]}",
        icon=folium.Icon(color="green")
        )
    fg.add_child(marker)


    st.write(f"## {str(fg)}")
    
    map_cetaceans = st_folium(
        m,
        feature_group_to_add=fg,
        center=st.session_state["center"],
        zoom=st.session_state["zoom"],
        width=500,
        height=500,
        returned_objects=['last_clicked', 'zoom', 'center', 'last_object_clicked'],
    )

    if all([map_cetaceans['last_clicked'],
            map_cetaceans['last_clicked'] != st.session_state["last_clicked"]]):
        # https://geemap.org/foliumap/#geemap.foliumap.Map.st_last_click
        st.session_state['last_clicked'] = map_cetaceans['last_clicked']
        st.session_state['center'] = (map_cetaceans['last_clicked']['lat'],
                                      map_cetaceans['last_clicked']['lng'])        
        marker = folium.Marker(
                    location=[st.session_state['last_clicked']['lat'],
                              st.session_state['last_clicked']['lng']],
                    popup='Something',
                    tooltip=f"{st.session_state["last_clicked"]}",
                    icon=folium.Icon(color="green")) 
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