import streamlit as st
import pandas as pd
import openai
import os
import matplotlib.pyplot as plt

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_KEY")

# Title and description
st.title("Data Analysis App")
st.write("Upload a CSV or Excel file for analysis.")

# File upload
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"])


data1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
data2 = [3, 4, 5, 6, 7, 2, 4, 345, 4, 54, 7, 6, 658, 1]

plt.plot(data1, data2)
plt.xlabel('Data 1')
plt.ylabel('Data 2')
plt.title('Data Analysis')
st.pyplot(plt.plot(data1, data2))

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
    analysis_request = "Write a working python code that creates a matplot figure object and plot it with st.pyplot(fig). Only write the python code and nothing else: " + data.to_string(index=False) + "Only write the python code and nothing else."

    if st.button("Generate Analysis Code"):
        # Create a conversation with a system message and user message
        conversation = [
            {"role": "system", "content": "You are a data analysis expert."},
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
