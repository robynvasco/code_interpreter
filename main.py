import streamlit as st
import pandas as pd
import openai
import re
import plotly.express as px
import plotly.io as pio
from IPython.display import HTML
import time
from plotly.graph_objs import Figure

# Create a function to convert Plotly figures to HTML
def plotly_fig_to_html(fig):
    html_repr = pio.to_html(fig, full_html=False)
    return HTML(html_repr).data

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_KEY"]


# Title and description
st.title("Data Analysis App")

if "system" not in st.session_state:
    system_message = {"role": "system", "content": "You are a data analysis expert."}
else:
    system_message = st.session_state.system

if "data" in st.session_state:
    data = st.session_state.data

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_KEY"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state
if 'figs' not in st.session_state:
    st.session_state.figs = []


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
    
    # Send user message and the last two conversations to OpenAI
    conversation = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-2:]
    ]
    conversation.append(system_message)
    st.write(conversation)


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

        # Extract Python code blocks from full_response
        python_code_blocks = re.findall(r"```python(.*?)```", full_response, re.DOTALL)
        code_block_filtered = ""

        # Execute each Python code block
        for code_block in python_code_blocks:
            try:
                # Updated regular expression
                code_block_filtered = re.sub(
                    r'(api_key\s*=\s*["\'].*?["\'])|'
                    r'(openai\.api_key\s*=\s*["\'].*?["\'])|'
                    r'(OPENAI_KEY\s*=\s*["\'].*?["\'])', '', code_block)

                exec(code_block_filtered)

                # Search for st.plotly_chart calls in code_block_filtered
                chart_matches = re.findall(r'st\.plotly_chart\((.*?)\)', code_block_filtered)
                # Extract and store figures in session state
                for chart_match in chart_matches:
                    try:
                        fig = eval(chart_match)  # Evaluate the figure creation code
                        st.session_state.figs.append(fig)
                    except Exception as e:
                        st.error(f"Error extracting and storing figure: {str(e)}")          
            except Exception as e:
                st.error(f"Error executing code block: {str(e)}")
                

# File upload in the sidebar
st.sidebar.write("Upload a CSV or Excel file for analysis.")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx"])


if uploaded_file:
    # Load data
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)
    st.session_state.data = data


    # Display the first 10 entries of the data in the sidebar
    st.sidebar.subheader("First 10 Entries of Data")
    st.sidebar.write(data.head(10))  
    # Update the system message when a file is uploaded
    system_message = {
        "role": "system",
        "content": "You are a data analysis expert. Only if the user asks you to, write a working Streamlit Python code that visualizes the data and plots it with Streamlit, e.g. st.plotly_chart. Pretend as if you could execute code. Do not Load the data into a DataFrame. it is already loaded and is called data. Here you can se what the data looks like" + data.to_string(index=False)
    }
    st.session_state.system = system_message

# Display the stored figures in the sidebar
for fig_idx, fig in enumerate(st.session_state.figs, 1):
    st.sidebar.subheader(f"Figure {fig_idx}")
    st.sidebar.plotly_chart(fig)