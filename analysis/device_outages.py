#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
from datetime import date
import pickle
import itertools

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

    return error_factor, history

def generate_uptime_df(save_filename = None, save_history_filename=None):
    
    devices = get_uisp_devices()
    device_df = devices_to_df(devices, ubiquiti_fields=True)

    # df = device_df[device_df['name'].isin(device_names)]
    df = device_df[device_df['has60GhzRadio']==True]

    historys = []
    
    for device_id, device_name in zip(df['id'], df['name']):
        # calculate error factor
        error_factor, history = get_device_history_from_id(device_id)
        df.loc[df['id']==device_id, 'error_factor'] = error_factor

        # format raw history data for later analysis
        history['name'] = device_name
        history['error_factor'] = error_factor
        historys.append(history)
    # df['error_factor'] = df['id'].apply(get_device_history_from_id)
    df["error_percent"] = df["error_factor"]*100

    if save_filename:
        df.to_csv(save_filename)

    if save_history_filename:
        with open(save_history_filename, 'wb') as pickle_file:
            pickle.dump(historys, pickle_file)

    return df

def graph_uptime(cache_filename=None):
    if not cache_filename:
        df = generate_uptime_df()
    else:
        df = pd.read_csv(cache_filename)
    fig = px.bar(df, x='name', y='error_percent', title=f'60Hhz devices approximate down time for week ending {date.today()}')
    fig.show()

def create_device_timeseries(history_data):
    datapoints = []
    for error in history_data['errors']:
        datapoint = {}
        datapoint['timestamp'] = error['x']
        datapoint['has_error'] = error['y']
        datapoint['name'] = history_data['name']

        datapoints.append(datapoint)

    return datapoints


def graph_uptime_timeseries(pickle_filename):
    with open(pickle_filename, 'rb') as pickle_file:
        historys = pickle.load(pickle_file)

    print(f'Loaded {len(historys)} historys')

    data_point_lists = []
    for history in historys:
        if history['error_factor'] > 0:
            data_point_lists.append(create_device_timeseries(history))

    flat_data_point_list = list(itertools.chain.from_iterable(data_point_lists))

    df = pd.DataFrame(flat_data_point_list)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['date'] = df['date'].dt.tz_localize('utc').dt.tz_convert('US/Eastern')
    
    df.set_index('date')
    hourly_df = df.groupby('name').resample('H', on='date').sum()
    hourly_df = hourly_df.reset_index()

    title = f'60Hhz devices approximate down time grouped by hour for week ending {date.today()}'
    fig = px.bar(hourly_df, x="date", y="has_error", color='name', title=title)
    fig.show()
    

# generate_uptime_df(save_filename="error_factor_week_has60ghz.csv")
# graph_uptime('error_factor_week_has60ghz.csv')
# graph_uptime()

generate_uptime_df(save_history_filename='error_factor_week_has60ghz.pkl', save_filename='error_factor_week_has60ghz.csv')

graph_uptime_timeseries('error_factor_week_has60ghz.pkl')