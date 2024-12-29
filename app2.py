import streamlit as st
import requests
import json
import pandas as pd
import streamlit as st
import matplotlib.cm as cm
import matplotlib.colors as colors
import folium
from streamlit_folium import st_folium

st.title('Netatmo Weather Data')

# Your credentials from the Netatmo developer console
CLIENT_ID = '64ec841e894f21eb880379d2'
CLIENT_SECRET = 'GgQXMy3UuYiQf8764QxqIu5krblSrplw6znQtrV'
REDIRECT_URI = 'http://localhost:8501/'

# Step 1: Generate the OAuth2 URL
oauth_url = f"https://api.netatmo.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read_station"
st.write(f"Click [here]({oauth_url}) to authorize the application.")


# Retrieve query parameters
query_params = st.experimental_get_query_params()
authorization_code = query_params.get('code')

# If authorization code is available
if authorization_code:
    authorization_code = authorization_code[0]  # Get the first item from the list
    st.write(f"Received authorization code: {authorization_code}")



    # Step 3: Obtain the access token
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI
    }
    token_r = requests.post('https://api.netatmo.com/oauth2/token', data=token_data)
    token_json = token_r.json()
    access_token = token_json['access_token']
    refresh_token = token_json['refresh_token']

    

    # Step 4: Make an API request to retrieve data
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.netatmo.com/api/getpublicdata?lat_ne=60.40&lon_ne=5.40&lat_sw=60.37&lon_sw=5.37&required_data=rain&filter=true', headers=headers)
    #st.write(json.dumps(response.json(), indent=2))

    #response = requests.get(f'https://api.netatmo.com/api/getpublicdata?lat_ne=62.6&lon_ne=12.0&lat_sw=59.3&lon_sw=5.59&required_data=rain&filter=true', headers=headers)

    data = response.json()

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


    st.dataframe(df_data)

    # Create a colormap
    norm = colors.Normalize(df_data['rain_24h'].min(), df_data['rain_24h'].max())
    cmap = cm.get_cmap("viridis")

    # Create a function to map rain_24h to a color
    def get_color(rain):
        rgba = cmap(norm(rain))
        return colors.rgb2hex(rgba)

    m = folium.Map(location=[60, 6], zoom_start=6)

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
    st_data = st_folium(m)