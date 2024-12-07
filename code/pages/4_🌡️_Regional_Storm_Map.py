import pandas as pd
import altair as alt
import plotly.graph_objects as go
import streamlit as st
import pycountry
import os

@st.cache_data
def load(url):
    return pd.read_json(url)


##########  Define relevant dictionaries for page ##############################################

country_dict = {} #record iso_3 codes for each country to fill in plotly map
for country in pycountry.countries:
    country_dict[country.name] = country.alpha_3

#append additional countries not in pycountry
country_dict['Russia'] = 'RUS'
country_dict['Congo (Democratic Republic Of The)'] = 'COD'
country_dict['Antigua And Barbuda'] = 'ATG'
country_dict['Bolivia'] = 'BOL'
country_dict['Bosnia And Herzegovina'] = 'BIH'
country_dict['British Virgin Islandsi'] = 'VGB'
country_dict["Côte D'Ivoire"] = 'CIV'
country_dict['Czech Republic'] = 'CZE'
country_dict['North Korea'] = 'PRK'
country_dict['South Korea'] = 'KOR'
country_dict['Venezuela'] = 'VEN'
country_dict['Burma'] = 'MMR'
country_dict['Guinea Bissau'] = 'GNB'
country_dict['Laos'] = 'LAO'
country_dict['Macedonia'] = 'MKD'
country_dict['Moldova'] = 'MDA'
country_dict['Swaziland'] = 'SWZ'
country_dict['Syria'] = 'SYR'
country_dict['Taiwan'] = 'TWN'
country_dict['Tanzania'] = 'TZA'
country_dict['Turkey'] = 'TUR'
country_dict['Vietnam'] = 'VNM'
country_dict['Iran'] = 'IRN'

basin_dict = {'CS': 'Caribbean Sea', 'GM': 'Gulf of Mexico','CP': 'Central Pacific', 'BB': 'Bay of Bengal',
              'AS': 'Arabian Sea','WA': 'Western Australia','EA': 'Eastern Australia','NA': 'North Atlantic',
              'SA': 'South Atlantic','NI':'North Indian','SI': 'South Indian','SP': 'Southern Pacific',
              'EP': 'Eastern North Pacific', 'WP': 'Western North Pacific'}


rev_basin_dict = {}
for b in basin_dict: rev_basin_dict[basin_dict[b]] = b

month_dict = {1: 'January', 2: 'February', 3 : 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10:'October', 11:'November', 12:' December'}

################################################################################################

##########  Read in and format data  ###########################################################
script_dir = os.path.dirname(os.path.abspath(__file__)) 
root_folder = os.path.dirname(script_dir)              

storm_csv = os.path.join(root_folder, "data", "storm_filtered_data.csv")
country_csv = os.path.join(root_folder, "data", "df_country.csv")
global_csv = os.path.join(root_folder, "data", "df_global.csv")

storm_df = pd.read_csv(storm_csv)
country_df = pd.read_csv(country_csv)
global_df = pd.read_csv(global_csv)

storm_df['ISO_TIME'] = pd.to_datetime(storm_df['ISO_TIME'])
storm_df['storm_month'] = storm_df['ISO_TIME'].dt.month
storm_df['BASIN'] = storm_df.apply(lambda x: x['SUBBASIN'] if pd.isna(x['BASIN']) else x['BASIN'],axis = 1)

country_df['dt'] = pd.to_datetime(country_df['dt'])
country_df['month'] = country_df['dt'].dt.month
country_df['year'] = country_df['dt'].dt.year

################################################################################################

st.set_page_config(page_title="Regional Temperatures and Storms", page_icon="🌡️", layout="wide")
st.title("🌡️ Regional Temperatures and Storms")
st.markdown("""
As global temperatures rise, regions of the world experience different storm seasons. Explore the globe below to see how **regional storm paths** have changed over the years, all inevitably affected by climate change. Please note that there is only temperature data up to August 2013, so the map will not display any temperature data for September 2013 onwards.
""")

########## Filter data for visuals  ############################################################
st.sidebar.header("🔧 Filters")

# Define year and month filters
year_slider = st.sidebar.slider("Season", storm_df["SEASON"].min(), country_df["year"].max(),country_df["year"].max())
month_slider = st.sidebar.slider("Month", 1,12,5)


# filter storm data based on the year and month sliders
filtered_df = storm_df[storm_df['SEASON'] == year_slider]
filtered_df = filtered_df[filtered_df['storm_month'] == month_slider]
filtered_df['start_time'] = filtered_df.groupby(['SEASON','NAME'])['ISO_TIME'].transform('min')
filtered_df['days_elapsed'] = filtered_df.apply(lambda x: x['ISO_TIME'] - x['start_time'],axis=1)


available_basins = filtered_df['BASIN'].unique() #get all basins with storm data in this filtered df

available_basins_list = []
for b in available_basins:
    if b is None: continue
    if pd.isna(b): continue
    if b == 'MM' :continue
    available_basins_list.append(basin_dict[b])

# project available basins in a multiselect filter
basin_select = st.sidebar.multiselect("Basins",available_basins_list,default=available_basins_list)
basin_select_keys = [rev_basin_dict[b] for b in basin_select]

filtered_df = filtered_df[filtered_df['BASIN'].isin(basin_select_keys)]



# filter country data accordingly
filtered_country_df = country_df[country_df['year'] == year_slider]
filtered_country_df = filtered_country_df[filtered_country_df['month'] == month_slider]
filtered_country_df['iso_3'] = filtered_country_df['Country'].apply(lambda x: country_dict[x] if x in country_dict else x)
################################################################################################

########## Create storm globe   ################################################################
fig = go.Figure()

fig.add_trace(go.Choropleth(
                locations=filtered_country_df['iso_3'],  
                text=filtered_country_df['Country'],
                z=filtered_country_df['AverageTemperature'],
                colorscale='rdbu_r',
                colorbar=dict(title="Average Temperature ",x=1.1,titleside="right"),
                hovertemplate = '<b>%{text}</b><br><b>Temperature: %{z}</b><extra></extra>'           
                ))


fig.add_trace(go.Scattergeo(
    lon = filtered_df['LON'],
    lat = filtered_df['LAT'],
    text = filtered_df['NAME'],
    hovertext=filtered_df['days_elapsed'].astype(str),
    customdata = filtered_df['USA_SSHS'],
    mode = 'markers',
    marker=dict(
        size=9,
        color=filtered_df['USA_SSHS'],  
        colorscale='Viridis',
        colorbar=dict(title="Storm Category", x=1.3,titleside="right"),
        
    ),
    hovertemplate = '<b>%{text}</b><br><b>Storm Category: %{customdata}</b><br><b>Elapsed Time: %{hovertext}</b><extra></extra>'
   
))

fig.update_layout(
    geo=dict(
        projection_type="natural earth", # Set the projection type
        bgcolor = 'rgba(0,0,0,0)',
        lataxis=dict(range=[-90, 90]),  # Set latitude range
        lonaxis=dict(range=[-180, 180])
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=600,
    width=18000   
)

globe_fig = st.plotly_chart(fig)

################################################################################################

########## Calculate metrics  ##################################################################

## most storms per basin that month

most_storms = filtered_df.groupby('BASIN')['SID'].nunique()
most_storms_current = most_storms.max()
most_storms_basin = most_storms.idxmax()
basin_storms_initial = storm_df[(storm_df['BASIN'] == most_storms_basin) & (storm_df['storm_month'] == month_slider)]
count_min_year = basin_storms_initial[basin_storms_initial['ISO_TIME'] == basin_storms_initial['ISO_TIME'].min()]['SEASON'].min()
monthly_storms_initial_year = basin_storms_initial[basin_storms_initial['SEASON'] == count_min_year]['SID'].nunique()
monthly_increase_storms = ((most_storms_current - monthly_storms_initial_year) / (monthly_storms_initial_year)) * 100 # final matric


## most storms per basin that year
most_yearly_storms = storm_df[storm_df['SEASON'] == year_slider].groupby('BASIN')['SID'].nunique()
most_storms_yearly_current = most_yearly_storms.max()
most_storms_yearly_basin = most_yearly_storms.idxmax()
basin_storms= storm_df[storm_df['BASIN'] == most_storms_yearly_basin]
count_basin_storms_first_year = basin_storms[basin_storms['ISO_TIME'] == basin_storms['ISO_TIME'].min()]['SEASON'].min()
basin_storms_initial_num = basin_storms[basin_storms['SEASON'] ==count_basin_storms_first_year]['SID'].nunique()
annual_storms =  basin_storms[basin_storms['SEASON'] == year_slider]['SID'].nunique()
yearly_increase_storms = ((annual_storms - basin_storms_initial_num) / basin_storms_initial_num) * 100 # final metric

          
## average intense storms per basin that month
most_intense_storms = filtered_df[filtered_df['USA_SSHS'] >= 0].groupby(['BASIN','NAME']).max()
most_intense_basins = most_intense_storms.groupby(['BASIN']).mean('USA_SSHS')
most_intense_basin_avg = most_intense_basins[most_intense_basins['USA_SSHS'] == most_intense_basins['USA_SSHS'].max()].reset_index()
most_intense_basin = most_intense_basin_avg['BASIN'].min()
basin_avg = most_intense_basin_avg['USA_SSHS'].min()
basin_storms_initial = storm_df[(storm_df['BASIN'] == most_intense_basin) & (storm_df['storm_month'] == month_slider)]
basin_storms_initial = basin_storms_initial[basin_storms_initial['USA_SSHS'] >= 0]
min_year = basin_storms_initial[basin_storms_initial['ISO_TIME'] == basin_storms_initial['ISO_TIME'].min()]['SEASON'].min()
avg_basin_intensity_initial = basin_storms_initial[basin_storms_initial['SEASON'] == min_year].groupby('NAME').max('USA_SSHS')
initial_avg = avg_basin_intensity_initial['USA_SSHS'].mean()
monthly_intensity_increase = (basin_avg - initial_avg) #final metric

## average intense storms per basin that year
most_intense_storms_yearly = storm_df[storm_df['SEASON']==year_slider][storm_df['USA_SSHS'] >= 0].groupby(['BASIN','NAME']).max('USA_SSHS')
most_intense_basins_yearly = most_intense_storms_yearly.groupby(['BASIN']).mean('USA_SSHS')
most_intense_basin_avg_yearly = most_intense_basins_yearly[most_intense_basins_yearly['USA_SSHS'] == most_intense_basins_yearly['USA_SSHS'].max()].reset_index()
most_intense_basin_yearly = most_intense_basin_avg_yearly['BASIN'].min()
basin_storms= storm_df[storm_df['BASIN'] == most_intense_basin_yearly]
basin_storms = basin_storms[basin_storms['USA_SSHS'] >= 0]
basin_storms_first_year = basin_storms[basin_storms['ISO_TIME'] == basin_storms['ISO_TIME'].min()]['SEASON'].min()
basin_storms_initial_avg = basin_storms[basin_storms['SEASON'] == basin_storms_first_year].groupby('NAME').max('USA_SSHS')
initial_yearly_avg = basin_storms_initial_avg['USA_SSHS'].mean() 
basin_storms_curr_avg = basin_storms[basin_storms['SEASON'] == year_slider].groupby('NAME').max('USA_SSHS')
curr_yearly_avg = basin_storms_curr_avg['USA_SSHS'].mean()
yearly_intensity_increase = (curr_yearly_avg - initial_yearly_avg) #final metric


################################################################################################

########## Display metrics  ####################################################################

st.write("")
st.markdown("### 🌟 Key Highlights")
col1, col2 = st.columns(2)

with col1:
    st.header("Monthly trends")
    st.metric("Most storms : {}".format(basin_dict[most_storms_basin]), f"{most_storms_current} Storms", "{}% since {}".format(round(monthly_increase_storms,2),count_min_year))
    st.metric("Most intense storms : {}".format(basin_dict[most_intense_basin]), f"{round(basin_avg,2)} Average", "{} from {}".format(round(monthly_intensity_increase,2),min_year))
with col2:
    st.header("Yearly trends")
    st.metric("Most storms : {}".format(basin_dict[most_storms_yearly_basin]), f"{most_storms_yearly_current} Storms", "{}% since {}".format(round(yearly_increase_storms,2),count_min_year))
    st.metric("Most intense storms : {}".format(basin_dict[most_intense_basin_yearly]), f"{round(curr_yearly_avg,2)} Average", "{} from {}".format(round(yearly_intensity_increase,2),count_min_year))


################################################################################################

########## Intensity/frequency graphs  #########################################################

st.write("")
st.write("")

on = st.toggle("Storm frequency") #toggle to switch between different y-axes (intensity or storm county)
expl_str = "storm intensity"
alt_y = "max(USA_SSHS):Q"
title = 'USA SSHS'

if on:
    expl_str = "storm frequency"
    alt_y = "distinct(SID):Q"
    title = 'Storm Count'

st.markdown("Explore individual basins below to see {} through the years in the month of {}.".format(expl_str,month_dict[month_slider]))

graph_df = storm_df[storm_df['SEASON'] <= year_slider]
graph_df = graph_df[graph_df['storm_month'] == month_slider]


graph_df = graph_df[graph_df['BASIN'].notna()]
graph_df = graph_df[graph_df['BASIN'] != 'MM']
graph_df = graph_df[graph_df['BASIN'].isin(basin_select_keys)]
graph_df['BASIN'] = graph_df['BASIN'].apply(lambda x: basin_dict[x])


area_chart = alt.Chart(graph_df).mark_area().encode(
        x = alt.X('SEASON:N',title="Year",axis=alt.Axis(grid=True,labelAngle=0)),
        y = alt.Y(alt_y,title=""),
        color = alt.Color("BASIN:N",legend=None)
    ).properties(height=100)

st.altair_chart(area_chart.encode(row=alt.Row("BASIN",header = alt.Header(title=title))))

################################################################################################

########## Futher text #########################################################################


st.write("")


with st.expander("🌍 What Can We Learn?"):
    st.markdown("""
    - **Regional Storms**: Certain basins may exhibit more activity than others in different seasons. Overall, the Western Pacific and North Indian Basin appear to be areas for frequent, intense storms.
    - **Global Warming and Hurricanes**: As we've seen earlier, it is difficult to directly correlate rising global temperatures and storm-related statistics. We can generally observe that that several basins have experienced an increase in storm frequency and intensity since 1980.
    - **Warm Countries and Storms**: We may observe that coastal countries with warmer land temperatures have more storm activity associated with them. This can especially be observed in the North Indian basin.
    """)


with st.expander("🗂️ View Raw Data"):
    st.write("Storm data")
    st.write(filtered_df)

    st.write("Country temperature data")
    st.write(filtered_country_df)

################################################################################################