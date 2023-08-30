import streamlit as st
import pandas as pd
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_KEY")

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

    # User input for analysis request
    analysis_request = st.text_input("Request for Analysis:", "")

    if st.button("Generate Analysis Code"):
        # Create a conversation with a system message and user message
        conversation = [
            {"role": "system", "content": "You are a data analysis assistant and give only the working code for the python script that could analyse and if possible visualize the data."},
            {"role": "user", "content": analysis_request}
        ]

        # Send the conversation to the GPT-3 API to generate analysis code
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        # Extract and display the analysis code
        analysis_code = response.choices[0].message["content"]
        st.subheader("Generated Analysis Code:")
        st.code(analysis_code, language="python")

        # Execute the analysis code
        try:
            exec(analysis_code)
        except Exception as e:
            st.error(f"Error executing analysis code: {str(e)}")
