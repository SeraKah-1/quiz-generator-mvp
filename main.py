import streamlit as st
from ui_modern import render_app_modern

st.set_page_config(page_title="Quiz Gen", page_icon="✏️", layout="centered")

if __name__ == "__main__":
    render_app_modern()