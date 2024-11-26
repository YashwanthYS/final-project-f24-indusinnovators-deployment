import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data


st.title("Global Storm Visualization")
st.markdown("This interactive dashboard demonstrates storms from where and when they originated and tracks them across their journey. This visualization helps explain the lifecycle of storms.")

df = pd.read_csv('storm_filtered_data.csv', skipinitialspace=True)

df['ISO_TIME'] = pd.to_datetime(df['ISO_TIME'])
df_daily = df.groupby(['SID', 'SEASON', 'NUMBER', df['ISO_TIME'].dt.date]).agg({
    'LAT': 'last',
    'LON': 'last',
    'NATURE': 'last',
    'USA_SSHS': 'max'
}).reset_index()
df_daily.rename(columns={'ISO_TIME': 'DATE'}, inplace=True)

size_mapping = {'TS': 100}  # Example size mapping
color_mapping = {'TS': 'red'}  # Example color mapping

# Slider for date selection
date_range = pd.to_datetime(df_daily['DATE']).dt.date.unique()
selected_date = st.slider("Select Date", min_value=min(date_range), max_value=max(date_range))

# Filter data for the selected date
selected_data = df_daily[df_daily['DATE'] == selected_date]

countries = alt.topo_feature(data.world_110m.url, 'countries')

sphere = alt.sphere()
graticule = alt.graticule()

final_chart = alt.layer(
    alt.Chart(sphere).mark_geoshape(fill='lightblue'),
    alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5),
    alt.Chart(countries).mark_geoshape(
        fill='ForestGreen',
        stroke='black'
    ),
    alt.Chart(selected_data).mark_circle(opacity=0.5).encode(
        longitude='LON:Q',
        latitude='LAT:Q',
        size=alt.Size('USA_SSHS:Q', scale=alt.Scale(range=[20, 1000], domain=[df_daily['USA_SSHS'].min(), df_daily['USA_SSHS'].max()])),
        color=alt.Color('NATURE:N', scale=alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values())))
    )
).project('equalEarth').properties(width=800,height=400)


# # Combine base map and storm points
# final_chart = (base_map + storm_points).properties(
#     width=800,
#     height=400
# )

st.altair_chart(final_chart)