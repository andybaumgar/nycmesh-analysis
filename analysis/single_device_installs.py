#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd

import mesh_database_client
from uisp_client import load_uisp_data_from_file, devices_to_df, get_uisp_devices

load_dotenv()

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

px.set_mapbox_access_token(os.environ.get('MAPBOX'))

def classify_single_device_install(device_name):
    device_name = device_name.lower()
    if('sxt' in device_name):
        return 'sxt'
    elif('lbe' in device_name):
        return 'lbe'
    elif('omni' in device_name):
        return 'omni'
    else:
        return 'other'

def get_signup_df_with_single_install_fields(uisp_data_file=None, uisp_data_file_cache_filename=None):

    if uisp_data_file:
            devices = load_uisp_data_from_file(uisp_data_file)
    elif uisp_data_file_cache_filename:
        devices = get_uisp_devices(save_filename="sxt_test.json")
    else:
        devices = get_uisp_devices()

    df = devices_to_df(devices)
    nn_count = df['nn'].value_counts()
    single_device_nns = list(nn_count[nn_count==1].index)
    print(486 in single_device_nns)
    single_devices_df = df[df['nn'].isin(single_device_nns)]

    single_devices_df['single_install_type'] = single_devices_df['name'].apply(classify_single_device_install)
    print(single_devices_df)
    print(single_devices_df.shape[0])

    single_nns = list(single_devices_df['nn'])
    install_sheet_single_sxt = database_client.signup_df[database_client.signup_df['NN'].isin(single_nns)]

    signup_df = install_sheet_single_sxt
    signup_df = signup_df[signup_df['NN'] > 0]
    signup_df['nn'] = signup_df['NN']

    signup_df = signup_df.merge(single_devices_df, on='nn', how='inner', suffixes=('_1', '_2'))

    signup_df = signup_df[signup_df['Status'].isin(['Installed'])]
    signup_df['timestamp_start'] = pd.to_datetime(signup_df['Timestamp'])
    signup_df['timestamp_end'] = signup_df['timestamp_start'] + pd.Timedelta(days=5)
    signup_df['diy'] = signup_df['notes'].str.contains('diy', case=False) | signup_df['notes2'].str.contains('diy', case=False) 

    return signup_df

def map_devices(signup_df_single_devices):
    fig = px.scatter_mapbox(
        signup_df_single_devices, 
        lat="Latitude", 
        lon="Longitude",   
        title=f"Single Device Installs",
        hover_name="NN",
        hover_data=['notes', 'notes2'],
        color="single_install_type",
        )

    fig.show()

def devices_timeline(signup_df_single_devices):

    fig = px.timeline(
        signup_df_single_devices, 
        x_start="timestamp_start", 
        x_end="timestamp_end", 
        y="single_install_type", 
        # y="Neighborhood", 
        hover_data=['NN', 'notes', 'notes2', 'ID'],
        color='diy',
        # color='Neighborhood',
        color_discrete_sequence=['rgba(255,0,0,0.5)', 'rgba(0,0,255,0.5)'],
        # height=400, 
        # width=1000, 
        title="Single Device Installs by Type"
    )
    fig.show()


if __name__ == "__main__":
    single_install_df = get_signup_df_with_single_install_fields(uisp_data_file='sxt_test.json')
    # map_devices(single_install_df)
    devices_timeline(single_install_df)
