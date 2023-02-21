#%%
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import re

from mesh_utils import nn_from_string

import mesh_database_client
from uisp_client import get_uisp_devices, get_data_file_path
from general_utils import human_timedelta, hours_delta

load_dotenv() 

sector_name = 'nycmesh-5916-west1'
sector_names = ['nycmesh-5916-south1', 'nycmesh-5916-south2', 'nycmesh-5916-west1', 'nycmesh-5916-west2', 'nycmesh-5916-east1']

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

px.set_mapbox_access_token(os.environ.get('MAPBOX'))

def get_lbe_df(devices, sector_names, database_client):
    lbes = []
    for device in devices:
        try:
            name = device['identification']['displayName']
            # if device['attributes']['apDevice']['name'] not in sector_names:
            if 'lbe' not in name:
                continue
            
            nn = database_client.get_nn(nn_from_string(name))
            if nn is None:
                continue
            location = database_client.nn_to_location(nn)
            last_seen = device['overview']['lastSeen']

            row = {
                'latitude': location['Latitude'],
                'longitude': location['Longitude'],
                # UISP location not used due to duplicate errors
                # 'latitude:':device['overview']['latitude'],
                # 'longitude':device['overview']['longitude'],
                'name': name,
                'lastSeen:':device['overview']['lastSeen'],
                'frequency':device['overview']['frequency'],
                'signal':device['overview']['signal'],
                'wirelessMode':device['overview']['wirelessMode'],
                'nn': nn,
                'ap':device['attributes']['apDevice']['name'],
                'lastSeen': device['overview']['lastSeen'],
                'lbe_ip':device['ipAddress'],
                # 'node_ip':nn_to_ip(nn)
            }

            lbes.append(row)
        except (KeyError, TypeError):
            continue

    df = pd.DataFrame.from_dict(lbes)
    df['lastSeen']= pd.to_datetime(df['lastSeen'])
    df['last_seen_human_readable']= df["lastSeen"].apply(human_timedelta)
    df['last_seen_hours']= df["lastSeen"].apply(hours_delta)

    return df

def get_sectors_df(devices, sector_names):

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
            continue
        
    df_sector = pd.DataFrame.from_dict(sectors)
    return df_sector

def show_lbe_stats(save_filename = None, save_csv=False, save_image=False, save_map_directory=False, show_sectors=False):
    if save_filename is None:
        raise ValueError('Filename required to write CSV and title Plot')
        
    df = get_lbe_df(devices, sector_names, database_client)

    df_sector = get_sectors_df(devices, sector_names)

    # filter LBE devices
    # df = df[df['last_seen_hours'] > 84]
    df = df[df['signal'] < -68]

    data_file_path = get_data_file_path(save_filename)
    data_time = re.findall(r'\d+', str(Path(data_file_path).stem))[0]

    lbe_stats_csv_path = str(Path(data_file_path).parent/data_time)+".csv"
    df.to_csv(lbe_stats_csv_path)
    print(f"LBE stats saved to {lbe_stats_csv_path}")

    title = f'Connected LBE Signal Strength {data_time} (UISP signal &lt; -68dBm)'

    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude",   
        color="signal", 
        # color="ap", 
        range_color = [-90, -50],
        color_continuous_scale=["red", "gray", "green"], 
        # zoom=11.8, 
        zoom=10, 
        title=title,
        hover_name="nn",
        hover_data=['ap', 'last_seen_hours'],
        center={"lat":40.693302,"lon":-73.974665}
        )

    fig.update_traces(marker=dict(size=12,),
                    selector=dict(mode='markers'))

    if show_sectors:
        fig.add_scattermapbox(
            lat=df_sector['latitude'],
            lon=df_sector['longitude'],
            marker=dict(size=12,color="gold"),
            showlegend=False
        )

    fig.show()

    if save_map_directory:

        html_path_object = Path(__file__).parent.parent / 'output' / f'{data_time}'
        try:
            os.mkdir(html_path_object)
        except Exception as e:
            pass
        html_path =  str(html_path_object / f'index.html')
        fig.write_html(html_path,
                    full_html=False,
                    include_plotlyjs='cdn')

    if save_image:
        image_path_object = Path(__file__).parent.parent / 'images'
        image_path =  str(image_path_object / f'{data_time}.png')
        fig.write_image(image_path, scale=6)

    # print(df.head())

if __name__ == "__main__":
    data_file_name = 'uisp_output_20230212.json'

    devices = get_uisp_devices(save_filename=data_file_name)    
    # devices = load_uisp_data_from_file(data_file_name)

    show_lbe_stats(save_filename=data_file_name, save_csv=True)