"""
This page is used to handle the data loading process. 

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-06
"""
from src.ExcelData import ExcelData  # Assuming the ExcelData class is in this module
import streamlit as st
import os


class DataHandler:

    def __init__(self) -> None:
        self.uploaded_data_file = None
        self.filepath_temp = os.path.join(".tempfiles", "temp_uploaded_file.xlsx")
        self.excel_data = None
        self.synchronized_data = None
        st.title("Data Loading")

    def load_data(self) -> None:
        """
        This function loads the data from the user selected file and stores it in session state.
        """
        # s0, prompt the user to upload the file
        self.uploaded_data_file = st.file_uploader("Upload .xlsx file", type="xlsx", accept_multiple_files=False)

        # s1, if the user has uploaded a file, save it to a temporary file
        if self.uploaded_data_file is not None:
            try:
                # Save the uploaded file to a temporary file
                with open(self.filepath_temp, "wb") as f:
                    f.write(self.uploaded_data_file.getbuffer())

            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")

        # s2, if the user has uploaded a file, process it using the ExcelData class
        if self.uploaded_data_file is not None:
            try:
                # Process the file using the ExcelData class
                self.excel_data = ExcelData(filepath=self.filepath_temp)
                self.synchronized_data = self.excel_data.df_sync  # Assuming df_sync is the synchronized data DataFrame

                st.session_state['data'] = self.synchronized_data
            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")

    def show_partial_data(self) -> None:
        """
        This function shows the partial data in the session state.
        """
        if 'data' in st.session_state:
            st.write("Data successfully loaded and processed!")
            # You can also display the data or some part of it here if you want
            st.dataframe(st.session_state['data'].head())


if __name__ == "__main__":

    datahandler = DataHandler()
    datahandler.load_data()
    datahandler.show_partial_data()

    # Load data if not already loaded
    # if 'data' not in st.session_state:
    #     st.session_state['data'] = None

    # load_data()

    # if st.session_state['data'] is not None:
    #     st.write("Data successfully loaded and processed!")
    #     # You can also display the data or some part of it here if you want
    #     st.dataframe(st.session_state['data'].head())
