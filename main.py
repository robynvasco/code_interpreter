import streamlit as st
import pandas as pd
import openai
import os
import matplotlib.pyplot as plt
import re
import plotly.express as px
import plotly.io as pio
from IPython.display import HTML
import time

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


# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_KEY"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a function to convert Plotly figures to HTML
def plotly_fig_to_html(fig):
    html_repr = pio.to_html(fig, full_html=False)
    return HTML(html_repr).data

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Send a message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Define the system message based on the presence of data
    if "data" in locals():
        system_message = {"role": "system", "content": "You are a data analysis expert. Only if the user asks you to, write a working Streamlit Python code that visualizes the data and plots it with Streamlit, e.g. st.plotly_chart. Pretend as if you could execute code. Do not Load the data into a DataFrame. it is already loaded and is called data. Here you can se what the data looks like" + data.to_string(index=False) }
    else:
        system_message = {"role": "system", "content": "You are a data analysis expert."}
    
    # Send user message and the last two conversations to OpenAI
    conversation = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]
    ]
    
    conversation.append(system_message)
    st.write(conversation)
    # Introduce a delay before displaying the full_response
    time.sleep(3)  # You can adjust the delay duration as needed
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
##

        # Extract Python code blocks from full_response
        python_code_blocks = re.findall(r"```python(.*?)```", full_response, re.DOTALL)

        # Execute each Python code block
        for code_block in python_code_blocks:
            try:
                code_block_filtered = re.sub(r'(api_key\s*=\s*["\'].*?["\'])|(openai\.api_key\s*=\s*["\'].*?["\'])|(OPENAI_KEY\s*=\s*["\'].*?["\'])', '', code_block)
                exec(code_block_filtered)
                st.write(code_block_filtered)

                # Check if the last executed code generated a Plotly figure
                if 'fig' in locals() and isinstance(fig, px.graph_objs._figure.Figure):
                    chart_html = plotly_fig_to_html(fig)
                    # Append the chart as an HTML representation to messages
                    st.session_state.messages.append({"role": "assistant", "content": chart_html})               
            except Exception as e:
                st.error(f"Error executing code block: {str(e)}")
        

            




   


