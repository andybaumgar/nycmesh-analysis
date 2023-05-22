#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
from datetime import date

import mesh_database_client
from analysis.uisp_client import load_uisp_data_from_file, devices_to_df, get_device_history, get_uisp_devices

device_names = ["nycmesh-713-af60xr-5916","nycmesh-3461-af60lr-5283","nycmesh-3461-af60lr-5916","nycmesh-1933-af60lr-1084","nycmesh-1340-af60lr-5916","nycmesh-713-af60lr-1635","nycmesh-1933-af60lr-7512","nycmesh-2282-af60lr-713","nycmesh-898-af60lr-7800","nycmesh-2463-gbep-507","nycmesh-1084-gbep-115","nycmesh-1084-gbep-1167","nycmesh-115-gbep-5712","nycmesh-1167-gbep-295","nycmesh-1340-gbelr-5014","nycmesh-135-gbep-898","nycmesh-1417-gbelr-3606","nycmesh-1932-gbelr-731","nycmesh-1933-gbep-1932","nycmesh-2090-gbelr-295","nycmesh-449-gbep-295","nycmesh-2463-gbep-2274","nycmesh-713-gbelr-5989","nycmesh-sn3-gbelr-2701"]

def get_error_factor(history):
    error_count = 0
    for error in history['errors']:
        if error['y']==1:
            error_count += 1

    error_factor = float(error_count)/float(len(history['errors']))

    return error_factor

def get_device_history_from_id(device_id, interval='week'):
    history = get_device_history(device_id, interval)
    error_factor = get_error_factor(history)

    return error_factor

def generate_uptime_df(save_filename = None):
    
    devices = get_uisp_devices()
    device_df = devices_to_df(devices, ubiquiti_fields=True)

    # df = device_df[device_df['name'].isin(device_names)]
    df = device_df[device_df['has60GhzRadio']==True]

    df['error_factor'] = df['id'].apply(get_device_history_from_id)
    df["error_percent"] = df["error_factor"]*100

    if save_filename:
        df.to_csv(save_filename)

    return df

def graph_uptime(filename):
    df = pd.read_csv(filename)
    df["error_percent"] = df["error_factor"]*100
    fig = px.bar(df, x='name', y='error_percent', title=f'60Hhz devices approximate down time for week ending {date.today()}')
    fig.show()

# generate_uptime_df(save_filename="error_factor_week_has60ghz.csv")
graph_uptime('error_factor_week_has60ghz.csv')