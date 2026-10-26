import calendar
import duckdb
import folium
import folium.features
import geopandas
import streamlit as st
from shapely.geometry import Point
from pathlib import Path
from streamlit_folium import st_folium
from folium.plugins import HeatMap

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
    db_path = Path(__file__).parent.parent / "data/marts/gbif_cetaceans_great_britain.db"
    duck = duckdb.connect(str(db_path))
    duck.sql("install spatial")
    duck.sql("load spatial")

    return duck


def duck_circle(cetaceans, lng, lat, radius, month_of_visit='January'):
    """
    Return a GEOJson of a polygon-"circle" around the specified coordinates
    having the specified radius in kilometres, and match all data points that
    intersect the polygon's area from the local cetaceans_gb table.  
    """
    # query duckdb from python
    #https://github.com/duckdb/duckdb-blog-examples/blob/main/duckdb_streamlit/utils.py

    # spatial join by distance
    #ST_DWithin(a, b, x)

    # inscribing a circle
    #https://duckdb.org/docs/2.0/core_extensions/spatial/functions#st_buffer
    #GEOMETRY ST_Buffer (geom GEOMETRY, distance DOUBLE, num_triangles INTEGER)

    circle_around_coords = geopandas.GeoSeries(
                            [Point(lng,
                                   lat)],
                            crs=4326).to_crs(3043).buffer(radius*1000).to_crs(4326)

    try:
        cetaceans.sql('''SET geometry_always_xy = true''')
        dataframe = cetaceans.sql('''select
                                        *,
                                        st_distance_spheroid(
                                            ST_Point(c.latitude, c.longitude),
                                            ST_Point($lat, $lng)) as d
                                        from cetaceans_gb as c
                                        where d < $radius
                                        and month = $month_of_visit
                                        and year = 2025;''',
                                        params={"lat": lat,
                                                "lng": lng,
                                                "radius": radius*1000,
                                                "month_of_visit": month_of_visit}).df()
    except Exception:
        dataframe = None
    return (circle_around_coords, dataframe)

@st.cache_resource
def duck_everything(_cetaceans):
    """
    Return the entire cetaceans_gb table as a dataframe
    """
    return _cetaceans.sql("select * from cetaceans_gb").df()


def main():

    cetaceans = duck()
    
    # https://docs.streamlit.io/develop/concepts/architecture/session-state#initialization
    if "center" not in st.session_state:
        st.session_state["center"] = (51.51305718496589+4, -0.09419110869791583-5)
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = 6
    if 'last_clicked' not in st.session_state:
        st.session_state['last_clicked'] = {'lat': st.session_state["center"][0],
                                            'lng': st.session_state["center"][1]}    

    st.header("Cetacean Holiday", divider=True)
    st.subheader('Blue areas denote more cetacean sightings.')

    m = folium.Map(location=(51.51305718496589+4,
                             -0.09419110869791583-5),
                    zoom_start=4)

    # FeatureGroup
    fg = folium.FeatureGroup(name='radius')
    
    if "HeatMap" not in st.session_state:
        entire_dataframe = duck_everything(cetaceans)
        headmap_data = []
        for index, row in entire_dataframe.iterrows():
            # most of these values go unused since heatmap doesn't support tooltips 
            year=row['year']
            month=row['month']
            day=row['day']
            individual_count=row['individualCount']
            common_name=row['commonName']
            latitude=row['latitude']
            longitude=row['longitude']
            date=row['date']
            headmap_data.append([latitude, longitude])
        st.session_state['HeatMap'] = headmap_data
    heatmap_gradient = {0: 'blue', 1: 'blue'}
    HeatMap(st.session_state['HeatMap'], gradient=heatmap_gradient, min_opacity=0.33, radius=10).add_to(m)


    left, right = st.columns([1, 1])

    with right:
        radius = st.slider("Click on your destination and select how far away you can spot cetaceans", 10, 100, 50, 10)
        st.write("I can spot cetaceans from ", radius, "kilometers away")

        pill_options = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August', 'September',
                'October', 'November', 'December']
        
        month_of_visit = st.pills("For which month are you planning your trip?",
                                pill_options, selection_mode='single',
                                default='January', wrap=True)
        st.write("I'm planning my trip for ", str(month_of_visit) + ".")

    marker = folium.Marker(
        location=[st.session_state['last_clicked']['lat'],
                    st.session_state['last_clicked']['lng']],
        popup=f"Cetacean-spotting radius: {radius} kilometres.\n\n\nMonth of visit: {month_of_visit}\n{st.session_state['last_clicked']['lng']}\n{st.session_state['last_clicked']['lat']}",
        tooltip='Your chosen destination. Click for details.',
        icon=folium.Icon(icon='anchor', prefix='fa', color='black')
        )
    fg.add_child(marker)

    month_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9,
                'October': 10, 'November': 11, 'December': 12, None: 0}

    (bounds, matches) = duck_circle(cetaceans,
                                    st.session_state['last_clicked']['lng'],
                                    st.session_state['last_clicked']['lat'],
                                    radius, month_dict[month_of_visit])
    circle = folium.features.GeoJson(bounds, style_function=lambda feature: {
        "fill": False,
        "color": "black",
        "weight": 2})
    fg.add_child(circle)
    with right:
        st.subheader('Probability of seeing one or more cetacean on a given day, ' +
                 'assuming a uniform distribution of sightings during the same month:')
        st.write(str(
                     int(100*float(matches['day'].nunique())/
                     calendar.monthrange(2025, month_dict[month_of_visit])[1])) + '%')
    st.write(matches)

    with left:
        map_cetaceans = st_folium(
            m,
            feature_group_to_add=fg,
            center=st.session_state["center"],
            zoom=st.session_state["zoom"],
            width=720,
            height=600, 
            returned_objects=['last_clicked', 'zoom', 'center'],
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
                    popup='Destination',
                    tooltip='Destination',
                    icon=folium.Icon(color="black", icon='anchor'))
        (bounds, matches) = duck_circle(cetaceans,
                                        st.session_state['last_clicked']['lng'],
                                        st.session_state['last_clicked']['lat'],
                                        radius, month_of_visit)
        circle = folium.features.GeoJson(bounds)
        st.rerun()

if __name__ == "__main__":
    main()