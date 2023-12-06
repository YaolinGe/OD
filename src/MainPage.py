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

st.title("OD Turning Data Analysis")

