import requests
import json
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd

import mesh_database_client
from analysis.mesh_utils import nn_from_string, nn_to_ip
from analysis.config import devices_endpoint, statistics_endpoint

load_dotenv() 

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

headers={'x-auth-token': os.environ.get('NYCMESH_TOOL_AUTH_TOKEN')}

def get_data_file_path(data_filename):
    data_path_object = Path(__file__).parent.parent / 'data'
    data_file_path =  str(data_path_object / data_filename)
    return data_file_path

def load_uisp_data_from_file(data_filename):
    data_file_path =  get_data_file_path(data_filename)
    f = open(data_file_path)
    devices = json.load(f)

    return devices

def get_uisp_devices(save_filename=None):

    response = requests.get(devices_endpoint, headers=headers, verify=False)

    devices = json.loads(response.content)

    if devices == []:
        raise ValueError('Problem downloading UISP devices.')
    
    if save_filename is not None:
        data_file_path =  get_data_file_path(save_filename)
        devices_json = json.dumps(devices)
        with open(data_file_path, "w") as outfile:
            outfile.write(devices_json)
        print(f'UISP devices data saved to {data_file_path}')

    return devices

def devices_to_df(devices, ubiquiti_fields=False):
    parsed_devices = []
    for device in devices:
        try:
            name = device['identification']['displayName']
            nn = database_client.get_nn(nn_from_string(name))
            if nn is None:
                continue
            # location = database_client.nn_to_location(nn)
            last_seen = device['overview']['lastSeen']

            row = {
                # 'latitude': location['Latitude'],
                # 'longitude': location['Longitude'],
                'name': name,
                'lastSeen':device['overview']['lastSeen'],
                'model':device['identification']['model'],
                'modelName':device['identification']['modelName'],
                'id':device['identification']['id'],
                'nn': nn,
                'ip':device['ipAddress'],
            }

            if ubiquiti_fields:
                row['frequency'] = device['overview']['frequency']
                row['has60GhzRadio'] = device['features']['has60GhzRadio']

            parsed_devices.append(row)
        except (KeyError, TypeError):
            continue
    
    df = pd.DataFrame.from_dict(parsed_devices)
    return df

def get_device_history(device_id, interval):
    endpoint = statistics_endpoint.format(device_id)
    params = {
    # "start": "1678598000000",
    "interval": interval,
    # "period":"3600000"
    }
    response = requests.get(endpoint, headers=headers, params=params, verify=False)
    history = json.loads(response.content)
    return history


if __name__ == "__main__":
    device_id = '673cb9d4-7365-4714-8129-1c38cd697988'
    history = get_device_history(device_id)

