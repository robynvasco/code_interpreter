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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Define the system message based on the presence of data
        if "data" in locals():
            system_message = {"role": "system", "content": "You are a data analysis expert. Only if the user asks you to, write a working Streamlit Python code that visualizes the data and plots it with Streamlit, e.g. st.plotly_chart."}
        else:
            system_message = {"role": "system", "content": "You are a data analysis expert."}
        
        # Send user message and the last two conversations to OpenAI
        conversation = [system_message]
        
        for m in st.session_state.messages[-3:-1]:
            conversation.append({"role": m["role"], "content": m["content"]})

        conversation.append({
            "role": st.session_state.messages[-1]["role"],
            "content": st.session_state.messages[-1]["content"]
        })

        st.write(conversation)


        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=conversation,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")

        # After the loop, display the full_response and append it to messages
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})




   


