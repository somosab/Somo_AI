import streamlit as st

# Security improvements
import os
import json

# Function to load configuration securely
def load_config():
    config_path = os.getenv('CONFIG_PATH', 'config.json')  # Load config from environment variable
    if not os.path.exists(config_path):
        st.error("Configuration file not found")
        return None
    with open(config_path) as f:
        return json.load(f)

# Initialize app layout
st.set_page_config(
    page_title='Somo AI',
    layout='centered',
    initial_sidebar_state='expanded'
)

st.title('Welcome to Somo AI v4')

# Config loading
config = load_config()
if config is None:
    st.stop()

# Sidebar toggle functionality
st.sidebar.title('Navigation')
selected_option = st.sidebar.radio('Go to:', ["Home", "About", "Contact"])

if selected_option == "Home":
    st.header("Home Page")
    # Add your home page content here
    st.write("This is the main content of your application.")

elif selected_option == "About":
    st.header("About Page")
    st.write("This section contains information about the application.")

elif selected_option == "Contact":
    st.header("Contact Page")
    st.write("Contact us at: info@somosab.com")

# Mobile responsiveness
st.write("### Responsive Design")
st.write("This app is designed to be responsive on all devices.")

# Error handling example
try:
    assert config['api_key'] is not None  # Example to check required config
except AssertionError:
    st.error("API key is missing from the configuration.")

# Add your application logic here and handle possible exceptions
#
# End of application code