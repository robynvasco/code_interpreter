import streamlit as st
import pandas as pd
import requests

# Title and description
st.title("Data Analysis App")
st.write("Upload a CSV or Excel file for analysis.")

# File upload
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)

    # Display the raw data
    st.subheader("Raw Data")
    st.write(data)

    # Send data to the API for analysis
    api_url = "YOUR_API_URL_HERE"
    response = requests.post(api_url, json={"data": data.to_dict()})
    analysis_code = response.json().get("analysis_code")

    # Display the analysis code
    st.subheader("Analysis Code")
    st.code(analysis_code)

    # Execute the analysis code
    try:
        exec(analysis_code)
    except Exception as e:
        st.error(f"Error executing analysis code: {str(e)}")

