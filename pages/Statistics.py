from Dashboard import chicago_crime_sidebar, load_districts_data, predictions

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

districts_df = load_districts_data()
districts_dict = districts_df.set_index('community')['area_num_1'].to_dict()
indices = pd.to_numeric(districts_df['area_num_1']).to_list()

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

def fetch_crime_predictions_for_district(date_to_predict, predictions):
    date_to_predict = date_to_predict.strftime('%Y-%m-%d')
    # api_url = f"https://chicago-crimes-tf-qnywvpba7q-ew.a.run.app/predict?date={date_to_predict}"
    # response = requests.get(api_url)

    predictions = predictions.query(f'Date_day=="{date_to_predict}"')
    pred_crime = predictions.crime_count.reset_index(drop = True)

    # sort again by order of geojson
    pred_crime = [np.round(pred_crime[i-1], 1) for i in indices]
    return pred_crime

pred_crime = fetch_crime_predictions_for_district(date_to_predict, predictions)

results = []
# Create a list to hold the results
for i in range(len(districts_dict)):
    results.append({'District': list(districts_dict.keys())[i], 'Crime Prediction': pred_crime[i]})

# Create a DataFrame for plotting
df = pd.DataFrame(results).sort_values("Crime Prediction", ascending = True)

# Plotting with Streamlit
if submit:
    fig = px.bar(df,
                 x='Crime Prediction',
                 y='District',
                 orientation='h',  # This makes the bar chart horizontal
                 title="Crime Prediction by District")

    # Customize the figure to make bars fatter
    fig.update_layout(
        height=1500,  # Adjust the overall height of the figure (increase for thicker bars)
        bargap=0.05   # Reduce the gap between bars (closer to zero makes bars thicker)
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)
