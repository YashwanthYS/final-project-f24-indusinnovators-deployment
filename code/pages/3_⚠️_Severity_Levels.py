import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

st.title("🌪️ Global Storm Severity Levels Visualization vs Yearly Changes")

storm_csv = "./data/storm_filtered_data.csv"

storm_df = pd.read_csv(storm_csv, index_col=0)

storm_df['ISO_TIME'] = pd.to_datetime(storm_df['ISO_TIME'])
storm_df['year'] = storm_df['ISO_TIME'].dt.year
storm_df_filtered = storm_df[~storm_df["USA_SSHS"].isin([-5, -4, -3, -2, -1, 0])]

st.write("This plot visually illustrates how hurricane severity has fluctuated over the years, providing an intuitive way to observe trends and patterns in hurricane intensity. Each circle on the chart represents a specific severity level for a given year, with the radius of each circle corresponding to the number of hurricanes at that level of intensity.")
st.write("Each category of hurricane intensity is identified by a measure of windspeed generated as shown in the legend.")

fig, ax = plt.subplots(figsize=(10, 6))

cols = st.columns(2)
with cols[0]:
    start_year, end_year = st.slider(
        "Range of Years",
        min_value=1980,
        max_value=2023,
        value=(2006, 2016),  # Default range
        step=1,
    )


filtered_data = storm_df_filtered[(storm_df_filtered["year"] >= start_year) & (storm_df_filtered["year"] <= end_year)]

# Aggregate counts per year and category
category_counts = filtered_data.groupby(["year", "USA_SSHS"]).agg(counts=("USA_SSHS", "sum")).reset_index()  
category_counts["counts"] = category_counts["counts"]*3000

# Altair plot
chart = alt.Chart(category_counts).mark_circle().encode(
    x=alt.X('year:O', sort='ascending', title='Year'),     
    y=alt.Y('USA_SSHS:O', sort='descending', title='Storm Categories'),          
    size=alt.Size('counts:Q', 
                  scale=alt.Scale(domain=[0, category_counts['counts'].max()], range=[3, 2100]), 
                  legend=None),   
    color=alt.Color('USA_SSHS:O', 
                   scale=alt.Scale(domain=[1, 2, 3, 4, 5], range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']), 
                   legend=alt.Legend(title="Storm Categories", 
                                     labelFontSize=15, 
                                     symbolSize=100, 
                                     values=[5, 4, 3, 2, 1], 
                                     labelExpr="datum.value == 1 ? '1 : 34 < W < 64' : datum.value == 2 ? '2 : 64 < W < 83' : datum.value == 3 ? '3 : 83 < W < 96' : datum.value == 4 ? '4 : 96 < W < 113' : '5 : 113 < W < 137'")),
    tooltip=['year', 'USA_SSHS', 'counts']  
).properties(
    title=f"Counts of Storm Categories (USA_SSHS) from {start_year} to {end_year}",
    width=800,
    height=400
).configure_mark(
    size=4000   
).configure_axis(
    grid=True,  
    domain=True,
    ticks=True,  
    titleFontSize=14,
    labelFontSize=14, 
    labelAngle=-45,
).configure_title(
    fontSize=16,  
    anchor='start' 
)

st.altair_chart(chart, use_container_width=True)

st.markdown("### Stacked Bar Chart: Storm Categories by Year")

storm_df_grouped = storm_df_filtered.groupby(["year", "USA_SSHS"]).agg(counts=("USA_SSHS", "sum")).reset_index()  

pivot_data = storm_df_grouped.pivot(index="year", columns="USA_SSHS", values="counts").fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))

pivot_data.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    colormap="tab20",  
    alpha=0.9  
)

ax.set_title("Counts of Storm Categories (USA_SSHS) by Year")
ax.set_xlabel("Year")
ax.set_ylabel("Counts")
ax.legend(title="USA_SSHS Categories")

st.pyplot(fig)