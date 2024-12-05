import streamlit as st
import base64

st.set_page_config(page_title="HomePage", page_icon="🌎", layout="wide")
st.header(":earth_africa: _Global Temperatures and Their Impact on Hurricanes and Storms_")

st.markdown("""
Welcome to the interactive platform for exploring the relationship between **global temperatures** and the **frequency and intensity of hurricanes and storms**. 
This project aims to analyze historical and current data to provide insights into how climatic factors influence these phenomena.
""")

file_ = open("images/homepage.gif", 'rb')
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

# Display the GIF using markdown
st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="gif">',
    unsafe_allow_html=True,
)

st.markdown("""
### Data Source
The data used in this project is compiled from reputable sources, including:
- [National Oceanic and Atmospheric Administration (NOAA)](https://www.noaa.gov/)
- [Temperature Data](https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data/data)
""")

st.markdown("""
### Explore the Dashboards
Use the sidebar on the left to navigate between dashboards. Each dashboard offers an in-depth exploration of different aspects:
- ⁠Trends in **global temperatures** over decades with hurricane counts.
- ⁠Storm life cycle (variation over each day)
- ⁠Severity levels of the storms over time
- **Regional** storm and temperature patterns over time
- ⁠Predictions of **future temperatures** and **hurricane season intensity** .
""")

st.markdown("""
Dive in and explore the data to uncover patterns and relationships. Your insights can contribute to a better understanding of climate dynamics and their impact on severe weather events.
""")
