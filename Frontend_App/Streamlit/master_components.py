import streamlit as st
from PIL import Image
import os

def changeCSS():
    st.markdown(
        f'''
        <style>
            .block-container {{
                max-width: 65rem
            }}
            .bk-root .bk-data-table {{
                font-size: 100% !important
            }}
        </style>
    ''', unsafe_allow_html=True)

def showEmptyState():
    st.write("");st.write("");st.write("");st.write("")
    col1, col2, col3, col4, col5 = st.columns(5)
    col3.image(Image.open(os.path.dirname(__file__) + "/assets/emptystateicon.png"))
    col3.markdown("<p style='text-align: center'>Nothing to See Here...</p>", unsafe_allow_html=True)

def showTrainState():
    st.write("");st.write("");st.write("");st.write("")
    col1, col2, col3, col4, col5 = st.columns(5)
    col3.image(Image.open(os.path.dirname(__file__) + "/assets/trainmodelicon.png"), use_column_width="always")
    col3.markdown("<p style='text-align: center'>Please click 'Press to Train Model' on the side to start process</p>", unsafe_allow_html=True)

def showEmptySearch():
    st.write("");st.write("");st.write("");st.write("")
    col1, col2, col3, col4, col5 = st.columns(5)
    col3.image(Image.open(os.path.dirname(__file__) + "/assets/emptysearchicon.png"), use_column_width="always")
    col3.markdown("<p style='text-align: center'>Start searching for course by filling up the form above!</p>", unsafe_allow_html=True)

