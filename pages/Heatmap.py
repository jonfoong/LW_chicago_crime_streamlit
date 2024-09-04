from Dashboard import chicago_crime_sidebar, load_districts_data

import streamlit as st
import pydeck as pdk
import requests
import pandas as pd
import json
import numpy as np

# General Settings
st.set_page_config(page_title="Chicago Crime Map Overview", page_icon="🗺️", layout="wide")

# Sidebar
chicago_crime_sidebar()

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

# Settings: Main page
col1, col2 = st.columns(2, vertical_alignment='bottom')

with col1:
    date_to_predict = st.date_input("Day to predict:", format="DD.MM.YYYY")
with col2:
    submit = st.button("Get crime prediction", 'prediction')

# Data
districts_df = load_districts_data()
districts_dict = districts_df.set_index('community')['area_num_1'].to_dict()
indices = pd.to_numeric(districts_df['area_num_1']).to_list()
districts_geojson = json.loads(districts_df.to_json())

def add_prediction(districts_geojson, date_to_predict):
    date_to_predict = date_to_predict.strftime('%Y-%m-%d')
    api_url = f"https://chicago-crimes-tf-qnywvpba7q-ew.a.run.app/predict?date={date_to_predict}"
    response = requests.get(api_url)
    pred_crime = [response.json()[i][date_to_predict] for i in districts_dict.values()]
    # sort again by order of geojson
    pred_crime = [np.round(pred_crime[i-1], 1) for i in indices]
    
    # Füge den Höhenwert für jedes Feature hinzu und sammle die Höhenwerte
    for i in range(len(districts_df)):
        #elevation = random.randint(1,100)
        districts_geojson['features'][i]['properties']['elevation'] = pred_crime[i]
    
    # Bestimme die minimale und maximale Höhe
    min_elevation = min(pred_crime)
    max_elevation = max(pred_crime)
    
    # Funktion zur Interpolation der Farben von grün (0,255,0) bis rot (255,0,0)
    def get_color(value, min_value, max_value):
        if max_value == min_value:
            # Falls alle Elevations gleich sind, setze eine Standardfarbe
            return [255, 255, 0]  # Gelb als Standardfarbe
        ratio = (value - min_value) / (max_value - min_value)
        red = int(255 * ratio)
        green = int(255 * (1 - ratio))
        return [red, green, 0]
    
    # Setze den colorcode basierend auf der Farbskala
    for feature in districts_geojson['features']:
        elevation = feature['properties']['elevation']
        feature['properties']['colorcode'] = get_color(elevation, min_elevation, max_elevation)
    
    return districts_geojson

updated_districts_geojson = add_prediction(districts_geojson, date_to_predict)

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
            # FillExtrusionLayer for 3D buildings
            pdk.Layer(
                'GeoJsonLayer',
                data=updated_districts_geojson,
                pickable=True,
                extruded=True,  # Make it extruded for all features
                elevation_scale=50,  # Adjust this scale as needed
                elevation_range=[0, 1000],  # Set the elevation range
                auto_highlight=True,
                get_fill_color="properties.colorcode",
                get_elevation="properties.elevation"
            )
        ],
        tooltip={
            "html": "<b>District:</b> {community}<br><b>Crime Prediction:</b> {elevation}",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    )

if submit:
    st.pydeck_chart(create_map(), use_container_width=True)
else:
    # Show map on initial load
    st.pydeck_chart(create_map(), use_container_width=True)