import streamlit as st
import pandas as pd
import pickle
from datetime import datetime
import folium
from streamlit_folium import st_folium
import uuid
import base64
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

rf_model_path = os.path.join(script_dir, "models", "random_forest_model.pkl")
scaler_path = os.path.join(script_dir, "models", "scaler.pkl")
svr_model_path = os.path.join(script_dir, "models", "svr_temperature_model.pkl")
predicted_values_path = os.path.join(script_dir, "models", "forecasted_temperatures.csv")

rf_model = pickle.load(open(rf_model_path, "rb"))
scaler = pickle.load(open(scaler_path, "rb"))
svr_model = pickle.load(open(svr_model_path, "rb"))
predicted_values_df = pd.read_csv(predicted_values_path)
predicted_values_df['Date'] = pd.to_datetime(predicted_values_df['Date'], errors='coerce')

data = {
    "Class": ["-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "5"],
    "Precision": [0.96, 0.88, 0.90, 0.94, 0.93, 0.92, 0.83, 0.79, 0.76, 0.88, 0.87],
    "Recall": [0.97, 0.93, 0.94, 0.92, 0.93, 0.91, 0.84, 0.79, 0.78, 0.86, 0.78],
    "F1-Score": [0.96, 0.91, 0.92, 0.93, 0.93, 0.91, 0.84, 0.79, 0.77, 0.87, 0.82],
    "Support": [7137, 763, 1997, 173, 13094, 12898, 3970, 2070, 1310, 1312, 248]
}

summary_data = {
    "Metric": ["Accuracy", "Macro Avg", "Weighted Avg"],
    "Precision": ["-", 0.88, 0.91],
    "Recall": ["-", 0.88, 0.91],
    "F1-Score": [0.91, 0.88, 0.91],
    "Support": [44972, 44972, 44972]
}

df_metrics = pd.DataFrame(data)
df_summary = pd.DataFrame(summary_data)

st.markdown(
    """
    <h1 style="text-align: center; line-height: 1.5;">
        🌡️ Temperature and 🌪️ Hurricane <br>
        Intensity Prediction (-5 to 5 Range)
    </h1>
    """,
    unsafe_allow_html=True
)


st.sidebar.header("⚙️ Input Parameters")

selected_date = st.sidebar.date_input("📅 Select Date", value=datetime.today())
month = selected_date.month
day_of_year = selected_date.timetuple().tm_yday
day = selected_date.day

st.sidebar.subheader("📍 Latitude and Longitude")
input_method = st.sidebar.radio("Select Input Method", ["Click on Map", "Enter Manually"])

if input_method == "Enter Manually":
    lat_input = st.sidebar.text_input("Enter Latitude")
    lon_input = st.sidebar.text_input("Enter Longitude")

predict_button = st.sidebar.button("Predict")

if 'last_clicked' not in st.session_state:
    st.session_state['last_clicked'] = None
if 'predicted_intensity' not in st.session_state:
    st.session_state['predicted_intensity'] = None
if 'predicted_temperature' not in st.session_state:
    st.session_state['predicted_temperature'] = None
if 'map_key' not in st.session_state:
    st.session_state['map_key'] = str(uuid.uuid4())

def encode_icon_to_base64(icon_path):
    with open(icon_path, "rb") as icon_file:
        return base64.b64encode(icon_file.read()).decode()

location_pin_icon_path = os.path.join(script_dir, "icons", "location-pin.png")
hurricane_icon_path = os.path.join(script_dir, "icons", "hurricane.png")

location_pin_base64 = encode_icon_to_base64(location_pin_icon_path)
hurricane_base64 = encode_icon_to_base64(hurricane_icon_path)

def create_map():
    m = folium.Map(
        location=[0, 0],  
        zoom_start=1.4,
        tiles="OpenStreetMap", 
        no_wrap=True 
    )
    
    if st.session_state['last_clicked']:
        lat = st.session_state['last_clicked'][0]
        lon = st.session_state['last_clicked'][1]

        if st.session_state['predicted_intensity'] is not None:
            hurricane_html = f'<img src="data:image/png;base64,{hurricane_base64}" style="width:30px;height:30px;">'
            icon = folium.DivIcon(html=hurricane_html)
            folium.Marker(
                [lat, lon],
                popup=f"Predicted Intensity: {st.session_state['predicted_intensity']}",
                icon=icon
            ).add_to(m)
        else:
            location_pin_html = f'<img src="data:image/png;base64,{location_pin_base64}" style="width:30px;height:30px;">'
            icon = folium.DivIcon(html=location_pin_html)
            folium.Marker(
                [lat, lon],
                tooltip="Selected Location",
                icon=icon
            ).add_to(m)

    return m

st.subheader("📍 Select Latitude and Longitude")
map_placeholder = st.empty()
coordinates_placeholder = st.empty()
prediction_placeholder = st.empty()

if input_method == "Click on Map":
    if 'map_initialized' not in st.session_state:
        st.session_state['map_initialized'] = True
        m = create_map()
    else:
        m = create_map()

    with map_placeholder:
        st_map = st_folium(m, width=700, height=500, key=st.session_state['map_key'])

    if st_map and st_map.get('last_clicked'):
        lat = st_map['last_clicked']['lat']
        lon = st_map['last_clicked']['lng']

        if st.session_state['last_clicked'] != (lat, lon):
            st.session_state['last_clicked'] = (lat, lon)
            st.session_state['predicted_intensity'] = None
            st.session_state['map_key'] = str(uuid.uuid4())

            m = create_map()
            with map_placeholder:
                st_folium(m, width=700, height=500, key=st.session_state['map_key'])

            coordinates_placeholder.write(f"Selected Location: Latitude {lat:.4f}, Longitude {lon:.4f}")

elif input_method == "Enter Manually":
    if lat_input and lon_input:
        try:
            lat = float(lat_input)
            lon = float(lon_input)
            st.session_state['last_clicked'] = (lat, lon)
            st.session_state['predicted_intensity'] = None
            coordinates_placeholder.write(f"Selected Location: Latitude {lat:.4f}, Longitude {lon:.4f}")
        except ValueError:
            st.error("Invalid latitude or longitude values. Please enter numeric values.")

elif st.session_state['last_clicked']:
    lat, lon = st.session_state['last_clicked']
    coordinates_placeholder.write(f"Selected Location: Latitude {lat:.4f}, Longitude {lon:.4f}")

if predict_button:
    if st.session_state['last_clicked'] is None:
        st.error("Please provide all inputs: Select a location on the map or enter manually.")
    else:
        try:
            lat, lon = st.session_state['last_clicked']
            lat = float(lat)
            lon = float(lon)

            temperature_row = predicted_values_df.loc[
                    (predicted_values_df['Date'].dt.year == selected_date.year) & 
                    (predicted_values_df['Date'].dt.month == selected_date.month), 
                    'Prediction'
            ]

            if len(temperature_row) > 0:
                predicted_temperature = temperature_row.values[0]
            else:
                predicted_temperature = 16.0

            st.session_state['predicted_temperature'] = predicted_temperature

            input_features = pd.DataFrame(
                [[lat, lon, predicted_temperature, month, day_of_year, day]],
                columns=['LAT', 'LON', 'LandAndOceanAverageTemperature', 'month', 'day_of_year', 'day']
            )

            input_features_scaled = scaler.transform(input_features)
            predicted_intensity = rf_model.predict(input_features_scaled)[0]

            st.session_state['predicted_intensity'] = predicted_intensity

            st.session_state['map_key'] = str(uuid.uuid4())
            m = create_map()
            with map_placeholder:
                st_folium(m, width=700, height=500, key=st.session_state['map_key'])

            prediction_placeholder.success(
                f"**Predicted Average Temperature:** {predicted_temperature:.2f}°C  \n"
                f"**Predicted Hurricane Intensity:** {predicted_intensity}"
            )

        except ValueError:
            st.error("Invalid inputs. Please ensure latitude and longitude are numeric.")


if st.session_state['predicted_intensity'] is not None and st.session_state['predicted_temperature'] is not None:
    prediction_placeholder.success(
        f"**Predicted Temperature:** {st.session_state['predicted_temperature']:.2f}°C  \n"
        f"**Predicted Hurricane Intensity:** {st.session_state['predicted_intensity']}"
    )

if st.session_state['last_clicked']:
    lat, lon = st.session_state['last_clicked']
    coordinates_placeholder.write(f"Selected Location: Latitude {lat:.4f}, Longitude {lon:.4f}")

st.markdown("---")
st.subheader("🌪️ Hurricane Intensity Scale and Insights")

with st.expander("Scale Details"):
    st.markdown("""
    ### Hurricane Intensity Scale:
    - **-5**: 🌀 Weakest hurricane or storm, minimal damage expected.
    - **5**: 🌊 Strongest hurricane, catastrophic damage expected.

    #### Why This Tool Matters:
    This predictive tool is designed to:
    - **🏠 Help communities prepare** for potential hurricanes.
    - **🛡️ Aid disaster management teams** in issuing timely warnings.
    - **📊 Provide critical insights** to plan evacuations and resource allocations effectively.
    - **💾 Save lives** by offering accurate predictions of hurricane intensity.
    """)

st.markdown("---")
with st.expander("🤖 Hurricane Intensity Predictor Model Details"):
    st.markdown("""
    ### 🔍 Overview:
    This tool utilizes a **Random Forest Model**, a robust and highly accurate machine learning algorithm. Below are its key performance metrics:
    
    ### 🔍 Actual Accuracy:
    - **Overall Accuracy**: **0.908 (90.8%)**

    ### 🎯 Relaxed Accuracy:
    - **Relaxed Accuracy (±1)**: **0.979 (97.9%)**
                
    """)

    st.markdown("### 📊 Detailed Classification Metrics")
    st.table(df_metrics)

    st.markdown("### 🎯 Summary Metrics")
    st.table(df_summary)

    st.markdown("""
    ### 🛡️ Key Takeaway:
    This combination of **high precision and recall** ensures that the model can reliably predict hurricane intensities, empowering communities and agencies to prepare better for extreme weather events.
    """)


    st.markdown("---")
with st.expander("🌡️ Temperature Prediction Model Details"):
    st.markdown("""
    ### 🔍 Overview:
    This tool utilizes a **Support Vector Regression (SVR)** model with an RBF kernel for accurate temperature predictions.
    Below are its performance metrics:
    
    ### 📉 Model Performance:
    - **Mean Absolute Error (MAE):** **0.0942**
    - **Root Mean Squared Error (RMSE):** **0.1228**
    """)

    st.markdown("""
    ### 📊 Prediction Visualization:
    The plot below compares the **actual temperatures** with the **predicted temperatures** for the test dataset:
    """)
    
    svr_image_path = os.path.join(script_dir, "icons", "svr_temperature_predictions.png")
    st.image(svr_image_path, caption="SVR Temperature Predictions", use_column_width=True)

    st.markdown("""
    ### 🛡️ Key Takeaway:
    The low error metrics demonstrate that the SVR model performs excellently in predicting temperatures,
    providing reliable inputs for the hurricane intensity prediction.
    """)