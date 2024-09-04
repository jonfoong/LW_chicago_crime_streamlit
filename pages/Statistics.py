from Dashboard import chicago_crime_sidebar, load_districts_data

import streamlit as st
import requests
import pandas as pd
import numpy as np

# Page setup
#st.set_page_config(page_title="Chicago Crime Statistics", page_icon="👮‍♂️", layout='wide')

# Sidebar
chicago_crime_sidebar("statistics")

# Header
st.title('Chicago Crime Statistics')

# Input Area
col1, col2 = st.columns(2, vertical_alignment='bottom')

with col1:
    date_to_predict = st.date_input("Day to predict:", format="DD.MM.YYYY")
with col2:
    submit = st.button("Get crime prediction")

# Data
districts_df = load_districts_data()
districts_dict = districts_df.set_index('community')['area_num_1'].to_dict()
indices = pd.to_numeric(districts_df['area_num_1']).to_list()

def fetch_crime_predictions_for_district(date_to_predict):
    date_to_predict = date_to_predict.strftime('%Y-%m-%d')
    api_url = f"https://chicago-crimes-tf-qnywvpba7q-ew.a.run.app/predict?date={date_to_predict}"
    response = requests.get(api_url)
    pred_crime = np.round([response.json()[i][date_to_predict] for i in districts_dict.values()], 1)
    # sort again by order of geojson
    pred_crime = [pred_crime[i-1] for i in indices]
    return pred_crime

pred_crime = fetch_crime_predictions_for_district(date_to_predict)

results = []
# Create a list to hold the results
for i in range(len(districts_dict)):
    results.append({'District': list(districts_dict.keys())[i], 'Crime Prediction': pred_crime[i]})

# Create a DataFrame for plotting
df = pd.DataFrame(results)

# Plotting with Streamlit
if submit:
    st.bar_chart(df.set_index('District')['Crime Prediction'])
