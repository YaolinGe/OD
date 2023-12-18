"""
This script is used to build the streamlit App for the bobben experiment.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-06
"""
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
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("Data Analysis")
age = st.slider("How old ", 0, 130, 25)
st.write("I am ", age, " old")

values = st.slider("select a range of values", 0, 100, (25, 50))
st.write("Hello", values)

import streamlit as st
from datetime import time

appointment = st.slider(
    "Schedule your appointment:",
    value=(time(11, 30), time(12, 45)))
st.write("You're scheduled for:", appointment)

import streamlit as st
from datetime import datetime

start_time = st.slider(
    "When do you start?",
    value=datetime(2020, 1, 1, 9, 30),
    format="MM/DD/YY - hh:mm")
st.write("Start time:", start_time)
import streamlit as st

color = st.select_slider(
    'Select a color of the rainbow',
    options=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
st.write('My favorite color is', color)

import streamlit as st

on = st.toggle('Activate feature')

if on:
    st.write('Feature activated!')


# img_file_buffer = st.camera_input("Take a picture")

# if img_file_buffer is not None:
#     # To read image file buffer as bytes:
#     bytes_data = img_file_buffer.getvalue()
#     # Check the type of bytes_data:
#     # Should output: <class 'bytes'>
#     st.write(type(bytes_data))
    
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

st.sidebar.write("hello")

cols = st.columns(4)
for col in cols: 
    col.write("te")