import requests
import json
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd

import mesh_database_client
from mesh_utils import nn_from_string, nn_to_ip

load_dotenv() 

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

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

    response = requests.get("https://uisp.mesh.nycmesh.net/nms/api/v2.1/devices", headers={'x-auth-token': os.environ.get('NYCMESH_TOOL_AUTH_TOKEN')}, verify=False)

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

def devices_to_df(devices):
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
                'lastSeen:':device['overview']['lastSeen'],
                'nn': nn,
                'ip':device['ipAddress'],
            }

            parsed_devices.append(row)
        except (KeyError, TypeError):
            continue
    
    df = pd.DataFrame.from_dict(parsed_devices)
    return df


if __name__ == "__main__":
    # devices = get_uisp_devices("sxt_test.json")
    devices = load_uisp_data_from_file("sxt_test.json")
    df = devices_to_df(devices)
    nn_count = df['nn'].value_counts()
    # single_device_nodes = nn_count[nn_count==1]
    # single_device_nodes = df_count[df_count[nn]==1]
    # df_summary = df_count.value_counts()

    single_device_nns = list(nn_count[nn_count==1].index)
    single_devices_df = df[df['nn'].isin(single_device_nns)]

    # print(single_device_nns)
    print(486 in single_device_nns)
