#%%
import os
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.express as px

from dotenv import load_dotenv

load_dotenv()

data_path_object = Path(__file__).parent.parent / 'data'
data_file_path =  str(data_path_object / 'uisp_output_20230115.json')
f = open(data_file_path)
devices = json.load(f)

sector_name = 'nycmesh-5916-east1'

selected_devices = []
for device in devices:
    try:
        if device['attributes']['apDevice']['name'] == sector_name:
            row = {
                'latitude': device['location']['latitude'],
                'longitude': device['location']['longitude'],
                'name': device['identification']['displayName'],
                'lastSeen:':device['overview']['lastSeen'],
                'frequency':device['overview']['frequency'],
                'signal':device['overview']['signal'],
                'wirelessMode':device['overview']['wirelessMode'],
            }
            selected_devices.append(row)
    except Exception as e:
        continue

df = pd.DataFrame.from_dict(selected_devices)

# m = folium.Map(df[['latitude', 'longitude']].mean().values.tolist())

# for lat, lon in zip(df['latitude'], df['longitude']):
#     folium.Marker([lat, lon]).add_to(m)

# sw = df[['latitude', 'longitude']].min().values.tolist()

# ne = df[['latitude', 'longitude']].max().values.tolist()

# m.fit_bounds([sw, ne]) 
# m

import plotly.express as px

title = f'{sector_name} LBE Signal Strength'
px.set_mapbox_access_token(os.environ.get('MAPBOX'))
fig = px.scatter_mapbox(df, lat="latitude", lon="longitude",     color="signal", color_continuous_scale=px.colors.cyclical.IceFire, zoom=12, title=title)
fig.show()
# %%
