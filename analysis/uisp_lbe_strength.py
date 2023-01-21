#%%
import os
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.express as px
import os
import re
from dotenv import load_dotenv
import plotly.express as px

import mesh_database_client

load_dotenv() 
spreadsheet_id = os.environ.get("SPREADSHEET_ID")

database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

def nn_from_string(input_string):
    return int(re.findall("(\d{3,})", input_string)[0])

data_path_object = Path(__file__).parent.parent / 'data'
data_file_path =  str(data_path_object / 'uisp_output_20230120.json')
# data_file_path =  str(data_path_object / 'uisp_output_20230115.json')
f = open(data_file_path)
devices = json.load(f)

sector_name = 'nycmesh-5916-west1'
sector_names = ['nycmesh-5916-south1', 'nycmesh-5916-south2', 'nycmesh-5916-west1', 'nycmesh-5916-west2', 'nycmesh-5916-east1']

lbes = []
for device in devices:
    try:
        # if device['attributes']['apDevice']['name'] != sector_name:
        if device['attributes']['apDevice']['name'] not in sector_names:
            continue
            
        name = device['identification']['displayName']
        nn = database_client.get_nn(nn_from_string(name))
        if nn is None:
            continue
        location = database_client.nn_to_location(nn)

        row = {
            'latitude': location['Latitude'],
            'longitude': location['Longitude'],
            # 'latitude:':device['overview']['latitude'],
            # 'longitude':device['overview']['longitude'],
            'name': name,
            'lastSeen:':device['overview']['lastSeen'],
            'frequency':device['overview']['frequency'],
            'signal':device['overview']['signal'],
            'wirelessMode':device['overview']['wirelessMode'],
            'nn': nn
        }

        lbes.append(row)
    except KeyError:
        pass


sectors = []
for device in devices:
    try:
        if device['identification']['displayName'] not in sector_names:
            continue

        row = {
            'latitude':device['location']['latitude'],
            'longitude':device['location']['longitude'],
            'name': device['identification']['displayName'],
        }

        sectors.append(row)
            
    except KeyError:
        pass

data_time = re.findall(r'\d+', str(Path(data_file_path).stem))[0]

df = pd.DataFrame.from_dict(lbes)
df_sector = pd.DataFrame.from_dict(sectors)

df.to_csv(str(data_path_object/data_time)+".csv")

# lbe figure

# title = f'{sector_name} LBE Signal Strength'1

title = f'Vernon Connected LBE Signal Strength - {data_time}'

px.set_mapbox_access_token(os.environ.get('MAPBOX'))

fig = px.scatter_mapbox(
    df, 
    lat="latitude", 
    lon="longitude",   
    color="signal", 
    range_color = [-50, -90],
    color_continuous_scale=["red", "gray", "green"], 
    zoom=11.8, 
    title=title,
    hover_name="nn",
    )

fig.update_traces(marker=dict(size=12,),
                  selector=dict(mode='markers'))

# sectors figure

fig.add_scattermapbox(
    lat=df_sector['latitude'],
    lon=df_sector['longitude'],
    marker=dict(size=12,color="gold"),
    showlegend=False
)

fig.show()

image_path_object = Path(__file__).parent.parent / 'images'
image_path =  str(image_path_object / f'{data_time}.png')
fig.write_image(image_path, scale=6)
# %%
