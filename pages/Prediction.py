import streamlit as st
import requests
import pandas as pd
from datetime import timedelta
from Dashboard import chicago_crime_sidebar, chicago_crime_header, load_districts_data

# Page setup
chicago_crime_header()

# Sidebar
chicago_crime_sidebar()

# Header
st.title('Chicago Crime Statistics')

# Input Area
col1, col2, col3 = st.columns(3, vertical_alignment='bottom')

with col1:
    date_to_predict_start = st.date_input("Start Date:", format="DD.MM.YYYY", key="date_start")
with col2:
    date_to_predict_end = st.date_input("End Date:", format="DD.MM.YYYY", key="date_end")
with col3:
    submit = st.button("Get Crime Predictions", key="prediction")

def fetch_crime_predictions_for_district(district, date):
    # Format date as a string for the API call
    date_str = date.strftime('%Y-%m-%d')
    api_url = f"https://chicagocrimes-22489836433.europe-west1.run.app/predict?predict_day={date_str}&district={district}"
    response = requests.get(api_url)
    # Check if 'n_crimes' is in the response, return 0 if not
    return response.json().get('n_crimes', 0)

# Load district data
districts_geojson = load_districts_data()
communities = [district['properties']['community'] for district in districts_geojson['features']]

# Initialize DataFrame
results = []

if submit:
    # Iterate through each day in the date range
    current_date = date_to_predict_start
    while current_date <= date_to_predict_end:
        # For each date, iterate through each district
        for community in communities:
            n_crimes = fetch_crime_predictions_for_district(community, current_date)
            results.append({'Date': current_date, 'Community': community, 'Predictions': n_crimes})
        
        # Move to the next day
        current_date += timedelta(days=1)

    df = pd.DataFrame(results)
    st.dataframe(df, hide_index=True, height=None)
else:
    st.write("Please select a date range and click the button to get predictions.")
