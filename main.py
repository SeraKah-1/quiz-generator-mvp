import streamlit as st
from ui_modern import render_app_modern

# Config Halaman (Harus di paling atas)
st.set_page_config(
    page_title="Quiz App", 
    page_icon="⚡", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

if __name__ == "__main__":
    render_app_modern()
