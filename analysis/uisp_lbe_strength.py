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
import humanize
import datetime as dt

import mesh_database_client

load_dotenv() 

sector_name = 'nycmesh-5916-west1'
sector_names = ['nycmesh-5916-south1', 'nycmesh-5916-south2', 'nycmesh-5916-west1', 'nycmesh-5916-west2', 'nycmesh-5916-east1']

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

data_path_object = Path(__file__).parent.parent / 'data'
# data_file_path =  str(data_path_object / 'uisp_output_20230125_snow_rain.json')
data_file_path =  str(data_path_object / 'uisp_output_20230206.json')
# data_file_path =  str(data_path_object / 'uisp_output_20230115.json')
f = open(data_file_path)
devices = json.load(f)

def nn_from_string(input_string):
    matches = re.findall("(\d{3,})", input_string)
    if not matches:
        return None

    return int(re.findall("(\d{3,})", input_string)[0])

def human_timedelta(time):
    # time - dt.datetime.now()
    return humanize.precisedelta(time - dt.datetime.now(dt.timezone.utc), suppress=["seconds", "minutes", "days"])

def hours_delta(time):
    delta = dt.datetime.now(dt.timezone.utc) - time
    hours = delta.total_seconds()/3600
    return hours

def nn_to_ip(nn):
    ip_fourth_octet=nn%100
    ip_third_octet=int((nn-ip_fourth_octet)/100)
    ip = f"10.69.{ip_third_octet}.{ip_fourth_octet}"
    return ip

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
            # last_seen = device['overview']['lastSeen']

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
                'nn': nn,
                'ap':device['attributes']['apDevice']['name'],
                'lastSeen': device['overview']['lastSeen'],
                'lbe_ip':device['ipAddress'],
                # 'node_ip':nn_to_ip(nn)
            }

            lbes.append(row)
        except KeyError:
            pass

    df = pd.DataFrame.from_dict(lbes)
    df['lastSeen']= pd.to_datetime(df['lastSeen'])
    df['last_seen_human']= df["lastSeen"].apply(human_timedelta)
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
            pass
        
    df_sector = pd.DataFrame.from_dict(sectors)
    return df_sector

if __name__ == "__main__":

    df = get_lbe_df(devices, sector_names, database_client)

    df_sector = get_sectors_df(devices, sector_names)

    # df = df[df['last_seen_hours'] > 84]
    df = df[df['signal'] < -68]

    # print(df['last_seen_hours'])
    # df.shape[0]

    data_time = re.findall(r'\d+', str(Path(data_file_path).stem))[0]

    df.to_csv(str(data_path_object/data_time)+".csv")

    # lbe figure

    # title = f'{sector_name} LBE Signal Strength'1

    title = f'Connected LBE Signal Strength {data_time} (UISP signal &lt; -68dBm)'

    px.set_mapbox_access_token(os.environ.get('MAPBOX'))

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
        hover_data=['ap', 'last_seen_human'],
        center={"lat":40.693302,"lon":-73.974665}
        )

    fig.update_traces(marker=dict(size=12,),
                    selector=dict(mode='markers'))

    # sectors figure

    # fig.add_scattermapbox(
    #     lat=df_sector['latitude'],
    #     lon=df_sector['longitude'],
    #     marker=dict(size=12,color="gold"),
    #     showlegend=False
    # )

    # fig.show()

    # html_path_object = Path(__file__).parent.parent / 'output' / f'{data_time}'
    # try:
    #     os.mkdir(html_path_object)
    # except Exception as e:
    #     pass
    # html_path =  str(html_path_object / f'index.html')
    # fig.write_html(html_path,
    #             full_html=False,
    #             include_plotlyjs='cdn')

    # image_path_object = Path(__file__).parent.parent / 'images'
    # image_path =  str(image_path_object / f'{data_time}.png')
    # fig.write_image(image_path, scale=6)

    print(df.head())