"""
This script is used to build the streamlit App for the bobben experiment.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-06
"""
from model.TemperatureData import TemperatureData
from view.TemperatureVisualizer import TemperatureVisualizer
from model.ODTurningData import ODTurningData
from view.ODTurningDataVisualizer import ODTurningDataVisualizer
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

datapath = os.getcwd() + "/data/"
data_loaded = False
temperature_cases = [8, 37, 45, 55, 65, 75, 85]
allfiles = os.listdir(datapath)
od_files = [f for f in allfiles if f.endswith(".xlsx")]
od_cases = [f.split(".")[0] for f in od_files]

st.title("Data Analysis App")

# s0, upload data file and save it into a file and read those files accordingly. 
with st.sidebar: 
    data_source = st.radio(
        "Set data source 👇",
        ["Temperature", "OD turning"],
        captions=["Temperature data for Bobben under difference cases", "OD turning project"],
        label_visibility="visible",
    )

    # add button to select a specific temperature case
    if data_source == "Temperature":
        temperature_case = st.selectbox(
            "Select a temperature case 👇",
            temperature_cases,
            index=0,
            format_func=lambda x: f"{x} ℃",
        )
        filename = datapath + f"temperature_{temperature_case}.csv"
        dataHandler = TemperatureData(filename)
        data = dataHandler.df
        data_loaded = True

        col1, col2 = st.columns(2)
        with col1:
            sensorI = st.checkbox("Sensor I", value=False)
        with col2:
            sensorII = st.checkbox("Sensor II", value=False)

        gradient_level = st.slider("Gradient level", min_value=1, max_value=5, value=1, step=1)

        timewindow = st.slider("Smooth time window", min_value=1, max_value=500, value=1, step=50)

    if data_source == "OD turning":
        od_cases = st.selectbox("Select a test case 👇",
                                od_cases,
                                index=0,
                                format_func=lambda x: f"{x}")
        filename = datapath + f"{od_cases}.xlsx"
        dataHandler = ODTurningData(filename)
        data = dataHandler.df
        data_loaded = True

if data_loaded:
    if data_source == "OD turning":
        st.write("Here comes OD turning dataset visualization.")
        odv = ODTurningDataVisualizer(data)
        odv.plot_item(y="Deflection")
        odv.plot_item(y="Load")
        odv.plot_item(y="Temperature")
        odv.plot_item(y="StrainGauge1")
        odv.plot_item(y="StrainGauge2")
    elif data_source == "Temperature":
        dataHandler.smooth_data(timewindow)
        tv = TemperatureVisualizer(data)
        if sensorI and sensorII:
            col1, col2 = st.columns(2)
            with col1:
                tv.plot_temperature(y="TemperatureSensorI")
                for i in range(gradient_level):
                    tv.plot_temperature(y=f"TemperatureSensorI_G{i + 1}")
            with col2:
                tv.plot_temperature(y="TemperatureSensorII")
                for i in range(gradient_level):
                    tv.plot_temperature(y=f"TemperatureSensorII_G{i + 1}")
        elif sensorI:
            tv.plot_temperature(y="TemperatureSensorI")
            for i in range(gradient_level):
                tv.plot_temperature(y=f"TemperatureSensorI_G{i + 1}")
        elif sensorII:
            tv.plot_temperature(y="TemperatureSensorII")
            for i in range(gradient_level):
                tv.plot_temperature(y=f"TemperatureSensorII_G{i + 1}")
        else:
            st.warning("Please select at least one sensor to plot.")
    else:
        st.warning("Please select a data source.")




        


        