from Dashboard import chicago_crime_sidebar, load_districts_data

import streamlit as st
import requests
import pandas as pd

# Page setup
st.set_page_config(page_title="Chicago Crime Statistics", page_icon="👮‍♂️", layout='wide')

# Sidebar
chicago_crime_sidebar()

# Header
st.title('Chicago Crime Statistics')

# Input Area
col1, col2 = st.columns(2, vertical_alignment='bottom')

with col1:
    date_to_predict = st.date_input("Day to predict:", format="DD.MM.YYYY")
with col2:
    submit = st.button("Get crime prediction")

# Data
districts_geojson = load_districts_data()
communities = [district['properties']['community'] for district in districts_geojson['features']]

def fetch_crime_predictions_for_district(district, date):
    api_url = f"https://chicagocrimes-22489836433.europe-west1.run.app/predict?predict_day={date}&district={district}"
    response = requests.get(api_url)
    return response.json().get('n_crimes', 0)  # Return 0 if 'n_crimes' is not in the response

# Create a list to hold the results
results = []

# For each district, get the prediction for the given date
for district in communities:
    n_crimes = fetch_crime_predictions_for_district(district, date_to_predict.strftime('%Y-%m-%d'))
    results.append({'District': district, 'Crime Prediction': n_crimes})

# Create a DataFrame for plotting
df = pd.DataFrame(results)

# Plotting with Streamlit
st.bar_chart(df.set_index('District')['Crime Prediction'])
