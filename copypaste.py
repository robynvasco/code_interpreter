import streamlit as st
import plotly.graph_objects as go
import re

# Example code block_filtered
code_block_filtered = """
fig1 = go.Bar(x=data['City'], y=data['Amount'], name='City vs Amount')
st.plotly_chart(fig1)

# Plotting Food vs Amount
fig2 = go.Bar(x=data['Food'], y=data['Amount.1'], name='Food vs Amount')
st.plotly_chart(fig2)
"""

# Initialize session state
if 'figs' not in st.session_state:
    st.session_state.figs = []

# Search for st.plotly_chart calls in code_block_filtered
chart_matches = re.findall(r'st\.plotly_chart\((.*?)\)', code_block_filtered)

# Extract and store figures in session state
for chart_match in chart_matches:
    try:
        fig = eval(chart_match)  # Evaluate the figure creation code
        st.session_state.figs.append(fig)
    except Exception as e:
        st.error(f"Error extracting and storing figure: {str(e)}")

# Example: Display the stored figures
for fig in st.session_state.figs:
    st.plotly_chart(fig)
