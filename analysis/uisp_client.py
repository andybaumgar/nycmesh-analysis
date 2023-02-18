import requests
import json
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv() 

def get_data_file_path(data_filename):
    data_path_object = Path(__file__).parent.parent / 'data'
    data_file_path =  str(data_path_object / data_filename)
    return data_file_path

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