from Dashboard import chicago_crime_sidebar, load_districts_data

import streamlit as st
import pydeck as pdk
import random
import requests
import pandas as pd

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
districts_geojson = load_districts_data()

def add_prediction(districts_geojson, date_to_predict):
    def fetch_crime_predictions(date_to_predict):
        api_url = f"https://chicagocrimes-22489836433.europe-west1.run.app/predict?predict_day={date_to_predict}"
        response = requests.get(api_url)
        return response.json()['n_crimes']
    
    elevations = []
    
    # Füge den Höhenwert für jedes Feature hinzu und sammle die Höhenwerte
    for feature in districts_geojson['features']:
        #elevation = fetch_crime_predictions(date_to_predict)
        elevation = random.randint(1,100)
        feature['properties']['elevation'] = elevation
        elevations.append(elevation)
    
    # Bestimme die minimale und maximale Höhe
    min_elevation = min(elevations)
    max_elevation = max(elevations)
    
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

# Creat the dataframe for table below
def extract_interesting_data(districts_geojson):
    # Extract relevant properties into a DataFrame
    data = []
    for feature in districts_geojson['features']:
        properties = feature['properties']
        data.append({
            'District': properties.get('community'),
            'Area Number': properties.get('area_numbe'),
            'Crime Prediction': properties.get('elevation'),
            'Color': properties.get('colorcode'),
        })

    df = pd.DataFrame(data)
    
    # Sort by Crime Prediction descending
    df = df.sort_values(by='Crime Prediction', ascending=False)
    
    return df
def color_cell(val):
    color = f'rgb({val[0]}, {val[1]}, {val[2]})'
    return f'background-color: {color}'

# Display table with filled color cells
df = extract_interesting_data(updated_districts_geojson)
df_styled = df.style.applymap(color_cell, subset=['Color'])

st.write("### Crime Predictions by District")
st.dataframe(df_styled.format({"Crime Prediction": "{:.0f}"}))