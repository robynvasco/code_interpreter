import streamlit as st
import pandas as pd
import openai
import os
import matplotlib.pyplot as plt

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_KEY"]



# File upload in the sidebar
st.sidebar.write("Upload a CSV or Excel file for analysis.")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)

    # Display the first 10 entries of the data in the sidebar
    st.sidebar.subheader("First 10 Entries of Data")
    st.sidebar.write(data.head(10))


# Title and description
st.title("Data Analysis App")

with st.echo():
    # Your Python code goes here
    a = 5
    b = 10
    result = a + b
    # Create some data for plotting
    x = [1, 2, 3, 4, 5]
    y = [10, 8, 15, 7, 12]

    # Create a Matplotlib plot
    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Simple Matplotlib Plot')

   


