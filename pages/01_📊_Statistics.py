import streamlit as st
import numpy as np
import pandas as pd
import requests

# Page setup
st.set_page_config(page_title="Chicago Crime Statistics", page_icon="👮‍♂️")

# API call
api_url = "https://chicagocrimes-22489836433.europe-west1.run.app"
response = requests.get(api_url)
st.write(response.json())
