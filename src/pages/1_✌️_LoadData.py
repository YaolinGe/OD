"""
This page is used to handle the data loading process. 

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-06
"""

import streamlit as st
import pandas as pd
from src.ExcelData import ExcelData  # Assuming the ExcelData class is in this module

def load_data():
    """
    This function is used to load the data from the user and store it in session state.
    It uses the ExcelData class for processing the data.

    :return: None
    """
    uploaded_data_file = st.file_uploader("Upload .xlsx file", type="xlsx", accept_multiple_files=False)
    if uploaded_data_file is not None:
        try:
            # Save the uploaded file to a temporary file
            with open("temp_uploaded_file.xlsx", "wb") as f:
                f.write(uploaded_data_file.getbuffer())

            # Process the file using the ExcelData class
            excel_data = ExcelData(filepath="temp_uploaded_file.xlsx")
            synchronized_data = excel_data.df_sync  # Assuming df_sync is the synchronized data DataFrame

            st.session_state['data'] = synchronized_data
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

# Load data if not already loaded
if 'data' not in st.session_state:
    st.session_state['data'] = None

load_data()

if st.session_state['data'] is not None:
    st.write("Data successfully loaded and processed!")
    # You can also display the data or some part of it here if you want
    st.dataframe(st.session_state['data'].head())
