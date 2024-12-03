import pandas as pd
import streamlit as st
import altair as alt
from scipy.stats import pearsonr

hurricane_data = pd.read_csv("./data/storm_filtered_data.csv")
temperature_data = pd.read_csv("./data/df_global.csv")

st.set_page_config(page_title="Climate Trends", page_icon="🌎", layout="wide")
st.title("🌎 Climate Trends: Hurricanes and Global Temperatures")
st.markdown("""
Explore the relationship between **hurricane occurrences** and **global temperature trends** from 1980 to 2013. Use the controls on the sidebar to filter data, choose what to display, and uncover insights about our changing planet. 🌍
""")

hurricane_data['ISO_TIME'] = pd.to_datetime(hurricane_data['ISO_TIME'])
hurricane_data['Year'] = hurricane_data['ISO_TIME'].dt.year
hurricane_data['Month'] = hurricane_data['ISO_TIME'].dt.month
hurricane_data['Month_Name'] = hurricane_data['ISO_TIME'].dt.strftime('%B')  
hurricane_data = hurricane_data[
    (hurricane_data['ISO_TIME'] >= '1980-01-01') & (hurricane_data['ISO_TIME'] <= '2013-12-31')
]

temperature_data['dt'] = pd.to_datetime(temperature_data['dt'])
temperature_data['Year'] = temperature_data['dt'].dt.year
temperature_data['Month'] = temperature_data['dt'].dt.month
temperature_data['Month_Name'] = temperature_data['dt'].dt.strftime('%B')  
temperature_data = temperature_data[
    (temperature_data['dt'] >= '1980-01-01') & (temperature_data['dt'] <= '2013-12-31')
]
average_temperatures = temperature_data.groupby(['Year', 'Month_Name']).agg(
    LandAverageTemperature=('LandAverageTemperature', 'mean'),
    LandAndOceanTemperature=('LandAndOceanAverageTemperature', 'mean')
).reset_index()

st.sidebar.header("🔧 Filters")
selected_year_range = st.sidebar.slider(
    "Select Year Range:",
    min_value=1980,
    max_value=2013,
    value=(1980, 2013),
    step=1
)
month_options = ["All Months"] + list(hurricane_data['Month_Name'].unique())
selected_month = st.sidebar.selectbox("Filter by Month:", options=month_options, index=0)
show_land_temp = st.sidebar.checkbox("Show Land Temperatures 🌍", value=True)
show_land_and_ocean_temp = st.sidebar.checkbox("Show Land and Ocean Temperatures 🌊", value=True)
show_hurricane_counts = st.sidebar.checkbox("Show Hurricane Counts 🌪️", value=True)

if selected_month != "All Months":
    hurricane_data_filtered = hurricane_data[hurricane_data['Month_Name'] == selected_month]
    average_temperatures_filtered = average_temperatures[average_temperatures['Month_Name'] == selected_month]
else:
    hurricane_data_filtered = hurricane_data
    average_temperatures_filtered = average_temperatures.groupby('Year').agg(
        LandAverageTemperature=('LandAverageTemperature', 'mean'),
        LandAndOceanTemperature=('LandAndOceanTemperature', 'mean')
    ).reset_index()

hurricane_counts = hurricane_data_filtered.groupby('Year')['SID'].nunique().reset_index(name='Hurricane_Count')

filtered_combined_data = pd.merge(average_temperatures_filtered, hurricane_counts, on='Year', how='inner')

temp_long = pd.melt(
    filtered_combined_data,
    id_vars=['Year', 'Hurricane_Count'],
    value_vars=['LandAverageTemperature', 'LandAndOceanTemperature'],
    var_name='Temperature_Type',
    value_name='Temperature'
)

filtered_temp_long = temp_long[
    (temp_long['Year'] >= selected_year_range[0]) & (temp_long['Year'] <= selected_year_range[1])
]

temp_types = []
if show_land_temp:
    temp_types.append('LandAverageTemperature')
if show_land_and_ocean_temp:
    temp_types.append('LandAndOceanTemperature')

filtered_temp_long = filtered_temp_long[filtered_temp_long['Temperature_Type'].isin(temp_types)]

if show_hurricane_counts and (show_land_temp or show_land_and_ocean_temp):
    temp_for_corr = filtered_temp_long.groupby('Year')['Temperature'].mean().reset_index()
    merged_for_corr = pd.merge(temp_for_corr, hurricane_counts, on='Year')
    corr_coef, _ = pearsonr(merged_for_corr['Temperature'], merged_for_corr['Hurricane_Count'])
    st.sidebar.markdown(f"**Correlation Coefficient:** {corr_coef:.2f}")

st.markdown("### 🌟 Key Highlights")
col1, col2, col3 = st.columns(3)
with col1:
    max_hurricane_year = hurricane_counts.loc[hurricane_counts['Hurricane_Count'].idxmax(), 'Year']
    max_hurricane_count = hurricane_counts['Hurricane_Count'].max()
    st.metric("Year with Most Hurricanes", max_hurricane_year, f"{max_hurricane_count} Hurricanes")
with col2:
    hottest_year = filtered_combined_data.loc[filtered_combined_data['LandAverageTemperature'].idxmax(), 'Year']
    hottest_temp = filtered_combined_data['LandAverageTemperature'].max()
    st.metric("Hottest Year (Land)", hottest_year, f"{hottest_temp:.2f} °C")
with col3:
    st.metric("Correlation Coefficient", f"{corr_coef:.2f}")

base = alt.Chart(filtered_temp_long).encode(
    x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0))
)

color_scale = alt.Scale(
    domain=['LandAverageTemperature', 'LandAndOceanTemperature'],
    range=['#FF6F61', '#6B5B95']
)

charts = []

if show_hurricane_counts:
    hurricane_bars = alt.Chart(filtered_combined_data).mark_bar(
        color='#88B04B', opacity=0.7
    ).encode(
        x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0)),
        y=alt.Y('Hurricane_Count:Q', axis=alt.Axis(title='Hurricane/Storm Count')),
        tooltip=['Year', 'Hurricane_Count']
    ).properties(
        width=700,
        height=400
    )
    charts.append(hurricane_bars)

if show_land_temp or show_land_and_ocean_temp:
    temp_selection = alt.selection_multi(fields=['Temperature_Type'], bind='legend')
    temperature_lines = base.mark_line(point=alt.OverlayMarkDef(color="white")).encode(
        y=alt.Y('Temperature:Q', axis=alt.Axis(title='Temperature (°C)', orient='right')),
        color=alt.Color('Temperature_Type:N', scale=color_scale, legend=alt.Legend(title="Temperature Type")),
        opacity=alt.condition(temp_selection, alt.value(1), alt.value(0.1)),
        tooltip=['Year', 'Temperature', 'Temperature_Type']
    ).properties(
        width=700,
        height=400
    ).add_selection(
        temp_selection
    )
    charts.append(temperature_lines)

if charts:
    final_chart = alt.layer(*charts).resolve_scale(
        y='independent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    ).interactive()
    st.altair_chart(final_chart, use_container_width=True)
else:
    st.warning("Please select at least one data series to display.")


st.markdown("## 📖 Insights")
st.markdown("""
- **Temperature Trends**: The line graphs display yearly variations in global land and land and ocean temperatures.
- **Hurricane Activity**: The bar chart illustrates yearly hurricane occurrences.
- **Correlation**: The correlation coefficient indicates the relationship between rising temperatures and hurricane activity.
""")

with st.expander("🌍 What Can We Learn?"):
    st.markdown("""
    - **Global Warming and Hurricanes**: Rising global temperatures may not have a direct positive correlation with the number of hurricanes. Instead, sudden changes or drops in temperature after a sharp rise could create conditions favorable for hurricane formation, likely due to atmospheric depressions caused by the rapid temperature shifts.
    - **Temperature Fluctuations and Hurricane Formation**: Temperature differences can cause disturbances in the atmosphere, contributing to the formation of more hurricanes in the following year.
    - **Interactive Exploration**: Use the controls to focus on specific years or months to uncover detailed relationships between temperature trends and hurricane activity.
    """)


with st.expander("🗂️ View Raw Data"):
    st.write(filtered_combined_data)

st.sidebar.header("📤 Upload Your Own Data")
uploaded_hurricane_data = st.sidebar.file_uploader("Upload Hurricane Data CSV", type="csv")
uploaded_temperature_data = st.sidebar.file_uploader("Upload Temperature Data CSV", type="csv")

if uploaded_hurricane_data:
    hurricane_data = pd.read_csv(uploaded_hurricane_data)
    st.sidebar.success("Hurricane data uploaded successfully!")

if uploaded_temperature_data:
    temperature_data = pd.read_csv(uploaded_temperature_data)
    st.sidebar.success("Temperature data uploaded successfully!")
