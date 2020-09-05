# Importing the required libraries
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Global Variables
DATE_TIME = "date/time"
DATA_URL = (
    "./Data/Motor_Vehicle_Collisions_NYC.csv"
)

# Title of the Web app
st.title("Motor Vehicle Collisions in New York City")

# Displays the text as a markdown
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze motor vehicle collisions in NYC 🗽💥🚗")

# Decorating the function with streamlit cache to optimize performance
# by storing the result of the function in a local cache
@st.cache(persist=True)
def load_data(nrows):
    """
        Function which loads the data, changes the column names to lowercase
        and changes the name of column crash_date_crash_time as date/time
    """

    # Loading the data
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[
                       ['CRASH_DATE', 'CRASH_TIME']])

    # Droping NA values
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

    # Converting the column names to lower case
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)

    # Renaming crash_date_crash_time column
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
    #data = data[['date/time', 'latitude', 'longitude']]

    return data


# Loading the data with 100,000 rows
# data = load_data(70000)
data = load_data(100000)

# Most injured people in NYC
st.header("Where are the most people injured in NYC?")

# Adjustable slider
injured_people = st.slider(
    "Number of persons injured in vehicle collisions", 0, 19)

# Values shown in map
st.map(data.query("injured_persons >= @injured_people")
       [["latitude", "longitude"]].dropna(how="any"))

# Collision at a given time in a day
st.header("How many collisions occur during a given time of day?")

# Adjustable slider
hour = st.slider("Hour to look at", 0, 23)
original_data = data
data = data[data[DATE_TIME].dt.hour == hour]
st.markdown("Vehicle collisions between %i:00 and %i:00" %
            (hour, (hour + 1) % 24))

# Midpoint of the latitude and longitude for setting initial view of map
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

# If this checkbox is clicked, raw data is shown
if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" %
                 (hour, (hour + 1) % 24))
    st.write(data)

# Breakdown of number of crashes between the time interval
# is shown in a bar graph
st.subheader("Breakdown by minute between %i:00 and %i:00" %
             (hour, (hour + 1) % 24))

# Filtering the data to be inbetween the time interval
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

# Plotting a bar chart
fig = px.bar(chart_data, x='minute', y='crashes',
             hover_data=['minute', 'crashes'], height=400)
st.write(fig)

# Top 5 dangerous streets for different classe
st.header("Top 5 dangerous streets by affected class")
select = st.selectbox(
    'Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

# If the selected class is pedestrian
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(
        by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

# If the selected class is cyclist
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(
        by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

# If the selected class is motorists
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(
        by=['injured_motorists'], ascending=False).dropna(how="any")[:5])