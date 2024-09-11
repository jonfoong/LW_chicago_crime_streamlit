import streamlit as st
import requests
from streamlit_lottie import st_lottie
import geopandas as gpd
from shapely.geometry import shape
import json
import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account

# Configuration of the site
st.set_page_config(page_title="Chicago Crime Prediction", page_icon="👮‍♂️", layout="wide")

def auth_to_gbq():

    credentials = service_account.Credentials.from_service_account_info(st.secrets)

    client = bigquery.Client(credentials=credentials)

    # load bigquery data

    query_load_raw_data = f"""
    SELECT *
    FROM
    `wagon-bootcamp-428814.chicago_crime.predictions_real`
    """
    query_out = client.query(query_load_raw_data)
    query_out.result()

    df = query_out.to_dataframe()
    return df

# Sidebar
def chicago_crime_sidebar(key):
    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    with st.sidebar:
        container = st.container()  # Container für die Lottie-Animation
        with container:
            lottie_hello = load_lottieurl("https://lottie.host/ddc9bd14-5703-49fa-884c-c9236a48405f/y32PAxRVIG.json")
            st_lottie(lottie_hello, key=key, height=150, width=100)

    st.sidebar.header("Menu")
    st.sidebar.page_link("Dashboard.py", label="Overview", icon="🚔")
    st.sidebar.page_link("pages/Statistics.py", label="Statistics", icon="💯")
    #st.sidebar.page_link("pages/Map.py", label="Map", icon="🗺️")
    st.sidebar.page_link("pages/Heatmap.py", label="Heatmap", icon="📊")

chicago_crime_sidebar("dashboard")

# General district data
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
    #districts_geojson = json.loads(districts.to_json())
    return districts

# Page content
st.title("Welcome to Chicago's Future Crime Analytics")

st.markdown("""This is our group's capstone project for Le Wagon's bootcamp in Data Science and AI in Python. The app uses Chicago crime data provided by the city of Chicago from 2001 to 2024 to generate crime predictions for a given day in a given community area in Chicago. The app is no longer maintained, though information on data and modeling can still be found [here](https://github.com/jonfoong/LW_chicago_crime_pred) 

""")

# Cut out to shorten the intro a bit:
#Nonetheless, it is crucial to acknowledge that unexpected events, like another public health crisis, episodes of civil unrest, or shifts in economic stability, can dramatically reshape the landscape of crime. While some effects, like those of the COVID-19 pandemic, may seem temporary, they could have long-lasting repercussions, such as changes in urban mobility or persistent educational deficits from school closures.
#The key takeaway is the need for caution and flexibility in crime forecasting. Models must be continuously updated to reflect new data and the evolving conditions of each community. This approach helps mitigate the inherent uncertainty in predicting scrime, ensuring that policies are responsive to both predictable trends and unforeseen challenges.
st_lottie("https://lottie.host/90eb7346-7c52-4a86-bb9c-6cd5b5d93800/3ciMAFX8GE.json",
          key="arrest", height=350, width=350)


# some variables to be passed to other pages

predictions = auth_to_gbq()
predictions['Date_day'] = predictions['Date_day'].astype(str)
predictions['community_area'] = predictions['community_area'].astype(int)
predictions = predictions.query('community_area!=0')

predictions = predictions.sort_values(["Date_day", "community_area"])
