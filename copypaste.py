import streamlit as st
import pandas as pd
import openai
import re
import plotly.express as px
import time
import numpy
import plotly.io as pio
from plotly.graph_objs import Figure
import requests
from bs4 import BeautifulSoup
import re
import openpyxl
import os


# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_KEY"]

# Function to fetch text content from a URL
def fetch_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return text
        else:
            return None
    except Exception as e:
        return None
# Function to extract URLs from text
def extract_urls(text):
    # Regular expression to match URLs (this is a simple example)
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

    
# Title and description
st.title("Data Analysis App")

if "system" not in st.session_state:
    system_message = {"role": "system", "content": "You are a data analysis expert."}
    st.session_state.system = system_message
else:
    system_message = st.session_state.system

if "data" in st.session_state:
    data = st.session_state.data
if "workbook" in st.session_state:
    workbook = st.session_state.workbook

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_KEY"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, dict):
        # This is a text message with a "role" key
        if message["role"] == "assistant":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        elif message["role"] == "user":
            with st.chat_message(message["role"]):
                st.write(message["content"])
    elif isinstance(message, tuple):
        chart_type, chart_content = message
        if chart_type == "plotly":
            # This is a Plotly chart, display it with the "assistant" role
            with st.chat_message("assistant"):
                st.plotly_chart(chart_content)
        elif chart_type == "bar":
            # This is a Plotly chart, display it with the "assistant" role
            with st.chat_message("assistant"):
                st.bar_chart(chart_content)

# Accept user input
if prompt := st.chat_input("Send a message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)
    # Extract URLs from the user's message
    urls = extract_urls(prompt)
    
    # Check if there are any URLs in the message
    if urls:
        system_message = {"role": "system", "content": "When you write code always assume that the text from the website is already stored in the variable named text_from_url."}
        for url in urls:
            text_from_url = fetch_text_from_url(url)
            
            if text_from_url:
                # Update the system message with the text from the URL
                system_message["content"] += f"\nText from the URL:\n{text_from_url}"
        system_message["content"] += f"\n Write python code for an streamlit app and always assume that the text from the website is already stored in the variable named text_from_url. Print text with st.write. "     
        st.session_state.system = system_message

    # Send user message and the last prompt to OpenAI
    conversation = [st.session_state.system]
    st.write(conversation)
    conversation.append(st.session_state.messages[-1])


    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=conversation,
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
        python_code_blocks = []
        # Extract Python code blocks from full_response
        python_code_blocks = re.findall(r"```python(.*?)```", full_response, re.DOTALL)
        code_block_filtered = ""
    if python_code_blocks:
        with st.chat_message("assistant"):
        # Execute each Python code block
            for code_block in python_code_blocks:
                try:
                    # Updated regular expression
                    code_block_filtered = re.sub(
                        r'(api_key\s*=\s*["\'].*?["\'])|'
                        r'(openai\.api_key\s*=\s*["\'].*?["\'])|'
                        r'(OPENAI_KEY\s*=\s*["\'].*?["\'])', '', code_block)
                    # List files in the directory before executing the code
                    before_execution = set(os.listdir())
                    exec(code_block_filtered)
                    # List files in the directory after executing the code
                    after_execution = set(os.listdir())
                    new_file_extensions = ['.xlsx', '.mp4', '.pdf']
                    # Identify newly created files with allowed extensions
                    new_files = [file for file in after_execution - before_execution if any(file.endswith(ext) for ext in new_file_extensions)]

                    if new_files:
                        st.markdown("### Download New Files:")
                        for new_file in new_files:
                            file_extension = os.path.splitext(new_file)[1]  # Get the file extension
                            mime_type = get_mime_type(file_extension)  # Function to get MIME type based on file extension
                            st.download_button(
                                label=f"Download {new_file}",
                                data=open(new_file, "rb").read(),
                                key=f"download-button-{new_file}",
                                file_name=new_file,
                                mime=mime_type,
                            )
                    else:
                        st.write("No new files with allowed extensions were created.")




                    # Search for st.plotly_chart and other chart function calls in code_block_filtered
                    chart_matches = re.findall(r'st\.(plotly_chart|bar_chart)\((.*?)\)', code_block_filtered)

                    # Extract and store figures in session state
                    for chart_function, chart_match in chart_matches:
                        try:
                            if chart_function == "plotly_chart":
                                # Ensure that chart_match is a valid Python expression
                                fig = eval(chart_match)  # Evaluate the figure creation code
                                # Append the tuple with chart type and content
                                st.session_state.messages.append(("plotly", fig))
                            elif chart_function == "bar_chart":
                                fig = eval(chart_match)
                                st.session_state.messages.append(("bar", fig))
                        except Exception as e:
                            st.error(f"Error extracting and storing chart: {str(e)}")
                except Exception as e:
                    st.error(f"Error executing code block: {str(e)}")
                    

# File upload in the sidebar
st.sidebar.write("Upload a CSV, Excel, Video or Picture for analysis and editing.")
# File Upload
accepted_formats = ["csv", "xlsx", "mp3", "wav", "ogg", "mp4", "avi", "mkv"]
uploaded_file = st.sidebar.file_uploader("Upload a file", type=accepted_formats)


if uploaded_file:
    # Load data
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        data = pd.read_excel(uploaded_file)
        workbook = openpyxl.load_workbook(uploaded_file)
        st.session_state.workbook = workbook
        st.session_state.data = data
        # Update the system message when a file is uploaded
        system_message = {
        "role": "system",
        "content": """
        You are a data analysis expert. When writing code always skip the Data loading step. Assume the data from the excel file is stored with the variables
        workbook = openpyxl.load_workbook(uploaded_file) and
        data = pd.read_excel(uploaded_file)
        Assume you are writing code for a streamlit app, so when the user ask you to plot something use st.plotly_chart
        Here you can see what the data looks like:\n""" + data.to_string(index=False)
        }
        st.session_state.system = system_message
    elif uploaded_file.type == "text/csv":
        data = pd.read_csv(uploaded_file)
        st.session_state.data = data
        # Update the system message when a file is uploaded
        system_message = {
        "role": "system",
        "content": """
        You are a data analysis expert. When writing code always skip the Data loading step. Assume the data from the csv file is stored with the variable called
        data.
        Assume you are writing code for a streamlit app, so when the user ask you to plot something use st.plotly_chart
        Here you can see what the data looks like:\n""" + data.to_string(index=False)
        }
        st.session_state.system = system_message
    else:
        st.error("Unsupported file type")
    

