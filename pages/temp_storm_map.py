import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
import streamlit as st



@st.cache_data
def load(url):
    return pd.read_json(url)



storm_csv = "../storm_filtered_data.csv"
country_csv = "../EDA_Global_Temp_Data/dataset/df_country.csv"
global_csv = "../EDA_Global_Temp_Data/dataset/df_global.csv"

storm_df = pd.read_csv(storm_csv)
country_df = pd.read_csv(country_csv)
global_df = pd.read_csv(global_csv)

storm_df['ISO_TIME'] = pd.to_datetime(storm_df['ISO_TIME'])
storm_df['storm_month'] = storm_df['ISO_TIME'].dt.month

global_df['dt'] = pd.to_datetime(global_df['dt'])
global_df['month'] = global_df['dt'].dt.month
global_df['year'] = global_df['dt'].dt.year



cmap = plt.get_cmap('viridis')
storm_colors = cmap(np.linspace(0, 1, 256))
plotly_colorscale = [[i / 255, f'rgb{tuple(int(c * 255) for c in color[:3])}'] for i, color in enumerate(storm_colors)]

global_cmap = plt.get_cmap('coolwarm')
norm = plt.Normalize(storm_df['USA_SSHS'].min(), storm_df['USA_SSHS'].max())
storm_df["colors"] = storm_df["USA_SSHS"].apply(lambda x: cmap(norm(x)))


land_min = min(global_df['LandAverageTemperature'].min(),global_df['LandAndOceanAverageTemperature'].min())
land_max = max(global_df['LandAverageTemperature'].max(),global_df['LandAndOceanAverageTemperature'].max())


global_norm = plt.Normalize(global_df['LandAndOceanAverageTemperature'].min(), global_df['LandAndOceanAverageTemperature'].max())
land_norm = plt.Normalize(land_min,land_max)


f, ax = plt.subplots(figsize = (2,4))
# cb = mpl.colorbar.ColorbarBase(ax, cmap=global_cmap, norm=global_norm, orientation='vertical')
cb = mpl.colorbar.ColorbarBase(ax,cmap=global_cmap, norm=land_norm,orientation='vertical')

global_df["lo_colors"] = global_df["LandAndOceanAverageTemperature"].apply(lambda x: global_cmap(land_norm(x)))
global_df["l_colors"] = global_df["LandAverageTemperature"].apply(lambda x: global_cmap(land_norm(x)))



st.header("Storms and Global Temperatures")


year_slider = st.slider("Season", storm_df["SEASON"].min(), global_df["year"].max(),global_df["year"].max())



month_slider = st.slider("Month", 1,12,5)

# year_slider = 2005
# month_slider = 7

filtered_df = storm_df[storm_df['SEASON'] == year_slider]
filtered_df = filtered_df[filtered_df['storm_month'] == month_slider]

filtered_global_df = global_df[global_df['year'] == year_slider]

filtered_global_df = filtered_global_df[filtered_global_df['month'] == month_slider]

vals = filtered_global_df['lo_colors'].values
str_val = 'rgba(' + ','.join([str(x) for x in vals[0]])+ ')'

vals = filtered_global_df['l_colors'].values
str_val2 = 'rgba(' + ','.join([str(x) for x in vals[0]])+ ')'




fig = px.scatter_geo(filtered_df, lat='LAT', lon='LON', 
                     hover_name='NAME', 
                     projection="equirectangular", color='USA_SSHS',
                     color_continuous_scale=px.colors.sequential.Viridis) #do orthographic in 3D


fig.update_geos(
    showcoastlines=True, coastlinecolor="Black",
    showland=True, landcolor=str_val2,
    showocean=True, oceancolor=str_val,bgcolor='rgba(0,0,0,0)'
)

# Display the map using Streamlit
c1 = st.plotly_chart(fig)
#c2 = st.pyplot(f)
# ocean_geo = gpd.GeoDataFrame({'geometry': [Polygon([(0, 0), (180, 0), (180, 90), (0, 90), (0, 0)])]}, crs='EPSG:4326')

# ocean_geo['color'] = filtered_global_df['colors'] # Set ocean color

# st.map(filtered_df,latitude="LAT",longitude="LON",color="colors")
# st.map(ocean_geo, color='color') 







