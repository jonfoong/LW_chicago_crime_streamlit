import streamlit as st
import numpy as np
import pandas as pd
import json
import requests
import pydeck as pdk
import geopandas as gpd
from shapely.geometry import shape

# General Settings
st.set_page_config(page_title="Chicago Crime Map Overview", page_icon="🗺️")

# Sidebar
st.sidebar.header('Settings')

# Map Style
map_style_options = {
    "Dark Mode": "mapbox://styles/mapbox/dark-v11",
    "Satellite View": "mapbox://styles/mapbox/satellite-v9",
    "Satellite with Streets": "mapbox://styles/mapbox/satellite-streets-v12",
    "Navigation Day": "mapbox://styles/mapbox/navigation-day-v1",
    "Navigation Night": "mapbox://styles/mapbox/navigation-night-v1"
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
    url = "https://data.cityofchicago.org/resource/igwz-8jzy.json"
    response = requests.get(url)
    districts_json = response.json()
    
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

## Create the interactive map only if the button is pressed
if submit:
    st.pydeck_chart(pdk.Deck(
        map_style=chicago_map_style,
        initial_view_state=pdk.ViewState(
            latitude=41.881832,
            longitude=-87.623177,
            zoom=10,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=districts_geojson,
                pickable=True,
                stroked=True,
                filled=True,
                extruded=False,
                line_width_min_pixels=2,
                get_line_color=[100, 100, 100],
                get_fill_color=f"properties.community == '{district_selected}' ? [192, 192, 255, 200] : [200, 200, 200, 50]"
            )
        ],
        tooltip={
            "html": "<b>District(No.):</b> {community} ({area_numbe})",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    ))
