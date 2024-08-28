import streamlit as st

import numpy as np
import pandas as pd

st.set_page_config(page_title="Chicago Crime Predication", page_icon="👮‍♂️")




def main():
    # builds the sidebar menu
    with st.sidebar:
        st.page_link('app.py', label='Individual Checker', icon='🔥')
        st.page_link('pages/page_01.py', label='Competition Checker', icon='🛡️')

    st.title(f'🛡️ Competition Checker')

    # your content
    st.title("Chicago Crime Prediction")

if __name__ == '__main__':
    main()