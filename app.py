import requests
#from requests_oauthlib import OAuth2Session
import pandas as pd
import streamlit as st
import json
import matplotlib.cm as cm
import matplotlib.colors as colors
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
st.set_page_config(layout="wide")

client_id = '64ec841e894f21eb880379d2'
client_secret = 'GgQXMy3UuYiQf8764QxqIu5krblSrplw6znQtrV'
st.header("Netatmo API - Rainfall")

token = '64ec8390d411b83aab09ce1d|0d48172cc55c8cefcd2540b9886d845b'
refresh_token = '64ec8390d411b83aab09ce1d|c0bbe7e7a5f6d0f01148a43239bf69aa'

@st.cache_data
def hent_data(token, lat_ne=61, lon_ne=7, lat_sw=59, lon_sw=4):
    headers = {"Authorization": f"Bearer {token}"}


    response = requests.get(f'https://api.netatmo.com/api/getpublicdata?lat_ne={lat_ne}&lon_ne={lon_ne}&lat_sw={lat_sw}&lon_sw={lon_sw}&required_data=rain&filter=true', headers=headers)
    print(response)
    st.write(response)
    data = response.json()
    print(data)

    _id = []
    longitude = []
    latitude = []
    rain_60min = []
    rain_24h = []
    rain_live = []

    # Loop through each record in the API response
    for record in data['body']:
        _id.append(record['_id'])
        longitude.append(record['place']['location'][0])
        latitude.append(record['place']['location'][1])
        
        # Looking for the measures that contain rain information
        for module_id, measures in record['measures'].items():
            if 'rain_60min' in measures:
                rain_60min.append(measures.get('rain_60min'))
                rain_24h.append(measures.get('rain_24h'))
                rain_live.append(measures.get('rain_live'))
                break  # Assuming only one module will contain rain info per record

    # Create the DataFrame using collected lists
    df_data = pd.DataFrame({
        '_id': _id,
        'longitude': longitude,
        'latitude': latitude,
        'rain_60min': rain_60min,
        'rain_24h': rain_24h,
        'rain_live': rain_live
    })

    return df_data
#st.dataframe(df_data)
df_data = hent_data(token)
# Create a colormap
norm = colors.Normalize(df_data['rain_24h'].min(), df_data['rain_24h'].max())
cmap = cm.get_cmap("viridis_r")

# Create a function to map rain_24h to a color
def get_color(rain):
    rgba = cmap(norm(rain))
    return colors.rgb2hex(rgba)

m = folium.Map(location=[60.35, 5.35], zoom_start=8, width=750, height=500)

# Add points to the map
for index, row in df_data.iterrows():
    color = get_color(row['rain_24h'])
    folium.CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=f"Nedbør 24h: {row['rain_24h']}"
    ).add_to(m)

# Show the map
template = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px;
    left: 50px;
    width: 200px;
    height: 40px; 
    z-index:9999;
    font-size:14px;
    ">
    <p><a style="color:#000000;">Nedbør 24h:</a></p>
    <p><a style="color:#fafa6e;">Min</a><a style="color:#000000;"> - </a><a style="color:#440154;">Max</a></p>
    <div style="
    background: linear-gradient(to left, #440154, #482878, #3e4a89, #31688e, #26828e, #1f9e89, #35b779, #6dcd59, #b4de2c, #fde725);
    width:100%;
    height: 10px;
    ">
    </div>
</div>
{% endmacro %}
""" 

# Create a branca element with the HTML template
macro = MacroElement()
macro._template = Template(template)

# Add the legend to the map
m.get_root().add_child(macro)
st_data = st_folium(m, width=1000)
#print(st_data)


# st.write('60 min')
# norm_60 = colors.Normalize(df_data['rain_60min'].min(), df_data['rain_60min'].max())
# cmap_60 = cm.get_cmap("viridis_r")
# # Create an HTML template for the legend
# m2 = folium.Map(location=[60.35, 5.35], zoom_start=8, width=750, height=500)

# # Add points to the map
# for index, row in df_data.iterrows():
#     color = get_color(row['rain_60min'])
#     folium.CircleMarker(
#         location=(row['latitude'], row['longitude']),
#         radius=5,
#         color=color,
#         fill=True,
#         fill_color=color,
#         fill_opacity=0.6,
#         popup=f"Nedbør 60min: {row['rain_60min']}"
#     ).add_to(m)

# # Show the map
# template = """
# {% macro html(this, kwargs) %}
# <div style="
#     position: fixed; 
#     bottom: 50px;
#     left: 50px;
#     width: 200px;
#     height: 40px; 
#     z-index:9999;
#     font-size:14px;
#     ">
#     <p><a style="color:#000000;">Nedbør 24h:</a></p>
#     <p><a style="color:#fafa6e;">Min</a><a style="color:#000000;"> - </a><a style="color:#440154;">Max</a></p>
#     <div style="
#     background: linear-gradient(to left, #440154, #482878, #3e4a89, #31688e, #26828e, #1f9e89, #35b779, #6dcd59, #b4de2c, #fde725);
#     width:100%;
#     height: 10px;
#     ">
#     </div>
# </div>
# {% endmacro %}
# """ 

# # Create a branca element with the HTML template
# macro = MacroElement()
# macro._template = Template(template)

# # Add the legend to the map
# m2.get_root().add_child(macro)
# st_data_60min = st_folium(m2, width=1000)

if st.button('refresh'):
    token_url = 'https://api.netatmo.com/oauth2/token'

    # Parameters for the POST request
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        # Make the POST request to get a new access token
        response = requests.post(token_url, data=payload)
        response.raise_for_status()  # Raise an error if the request failed

        # Extract the access token from the response
        data = response.json()
        access_token = data['access_token']
        expires_in = data['expires_in']
        new_refresh_token = data['refresh_token']

        print(f"Access Token: {access_token}")
        print(f"Expires In: {expires_in} seconds")
        print(f"New Refresh Token: {new_refresh_token}")

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(e)