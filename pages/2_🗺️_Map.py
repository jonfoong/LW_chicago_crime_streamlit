import streamlit as st
import json
import pydeck as pdk
import geopandas as gpd
from shapely.geometry import shape
from streamlit_plotly_mapbox_events import plotly_mapbox_events

# General Settings
st.set_page_config(page_title="Chicago Crime Map Overview", page_icon="🗺️", layout="wide")

# Sidebar
st.sidebar.header('Settings')

# Map Style
map_style_options = {
    "Satellite with Streets": "mapbox://styles/mapbox/satellite-streets-v12",
    "Satellite": "mapbox://styles/mapbox/satellite-v9",
    "Dark Mode": "mapbox://styles/mapbox/dark-v11",
    "Navigation Day": "mapbox://styles/mapbox/navigation-day-v1",
    "Navigation Night": "mapbox://styles/mapbox/navigation-night-v1",
    "Street View": "mapbox://styles/mapbox/streets-v11",
    "Light v10": "mapbox://styles/mapbox/light-v10",
}
selected_style_name = st.sidebar.selectbox(
    "Select your map style:",
    list(map_style_options.keys())  # Shows keys of the dict as dropdown
)
chicago_map_style = map_style_options[selected_style_name] # Access Mapbox-Style-URL

# Page content
st.title('Chicago Crime Map')

@st.cache_data
def load_districts_data():
    # Pfad zur lokalen JSON-Datei
    file_path = 'data/geodata.json'
    
    # Daten aus der lokalen Datei lesen
    with open(file_path, 'r', encoding='utf-8') as file:
        districts_json = json.load(file)
    
    # Capitalize the community names in the JSON data
    for district in districts_json:
        if 'community' in district:
            district['community'] = district['community'].title()
    
    # Create GeoDataFrame
    districts = gpd.GeoDataFrame.from_features([{
        'geometry': shape(district['the_geom']),
        'properties': district
    } for district in districts_json])
    
    # Change GeoDataFrame in GeoJSON-Format
    districts_geojson = json.loads(districts.to_json())
    return districts_geojson

## Settings: Main page
col1, col2, col3 = st.columns(3, vertical_alignment='bottom')

with col1:
    days_to_predict = st.number_input("Days to predict:", value=7)
with col2:
    districts_geojson = load_districts_data()  # Ensure data is loaded here
    communities = [feature['properties']['community'] for feature in districts_geojson['features']]
    district_selected = st.selectbox(
        "Which district do you want to look at?",
        list(communities),
    )
with col3:
    submit = st.button("Get crime prediction", 'prediction')

# Input warning
if days_to_predict >= 30:
    st.warning("Please bear in mind that long-term forecasts are becoming less accurate!", icon="⚠️")

# Create the interactive map for initial load and when button is pressed
def create_map():
    return pdk.Deck(
        map_style=chicago_map_style,
        initial_view_state=pdk.ViewState(
            latitude=41.881832,
            longitude=-87.623177,
            zoom=10,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=districts_geojson,
                pickable=True,
                stroked=False,
                filled=True,
                extruded=True,  # Make it extruded for all features
                elevation_scale=50,  # Adjust this scale as needed
                elevation_range=[0, 1000],  # Set the elevation range
                get_line_color=[255, 0, 0],
                auto_highlight=True,
                coverage=1,
                get_line_width=40,  # Set the line width
                get_fill_color=f"properties.community == '{district_selected}' ? [192, 192, 255, 200] : [192, 192, 255, 100]",
                get_elevation=f"properties.community == '{district_selected}' ? 20 : 0",  # Dynamic elevation,
            )
        ],
        tooltip={
            "html": "<b>District(No.):</b> {community} ({area_numbe})",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    )

if submit:
    st.pydeck_chart(create_map(), use_container_width=True)
else:
    # Show map on initial load
    st.pydeck_chart(create_map(), use_container_width=True)
