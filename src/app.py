"""
This script is used to build the streamlit App for the bobben experiment.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-06
"""
from ExcelData import ExcelData
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
import seaborn as sns
from matplotlib.gridspec import GridSpec
import matplotlib as mpl
from tqdm import tqdm
import streamlit as st


st.set_page_config(
    page_title="Data Analysis App",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.google.com',
        'Report a bug': "https://www.geyaolin.com",
        'About': "# This is Data Analysis App. Designed and made by Yaolin!"
    }
)

data_loaded = False

st.title("Data Analysis App")

# s0, upload data file and save it into a file and read those files accordingly. 
with st.sidebar: 
    uploaded_file = st.file_uploader("Upload data file", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            filepath_temp = os.path.join(".tempfiles", "temp_uploaded_file.csv")
        elif uploaded_file.name.endswith(".xlsx"):
            filepath_temp = os.path.join(".tempfiles", "temp_uploaded_file.xlsx")
        else:
            filepath_temp = None
        try:
            with open(filepath_temp, "wb") as f:
                f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

    if uploaded_file is not None:
        dataHandler = ExcelData(filepath=filepath_temp)
        data = dataHandler.df_sync
        show_data = st.toggle("Show data")
        if show_data: 
            st.dataframe(data, hide_index=True, )
        else: 
            st.write("Data not shown.")
        # if st.button("Show data"):
        #     st.dataframe(data, hide_index=True, )
        # st.dataframe(data, hide_index=True, )

