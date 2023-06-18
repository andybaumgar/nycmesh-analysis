#%%
import pandas as pd
from datetime import date
import pickle
import itertools
import plotly.graph_objects as go
from plotly.colors import n_colors

from analysis.uisp_client import load_uisp_data_from_file, devices_to_df, get_device_history, get_uisp_devices


def get_60_ghz_interface(history):
    for interface in history['interfaces']:
        if interface['id'] == 'main':
            return interface

def get_60_ghz_down_factor(history):
    try:
        down_count = 0
        timeseries = get_60_ghz_interface(history)['transmit']
        for timestep in timeseries:
            if timestep['y']==0:
                down_count += 1

        down_factor_60ghz = float(down_count)/float(len(timeseries))

        return down_factor_60ghz
    except:
        return None

def get_device_histories(save_filename = None, save_history_filename=None, interval='week'):
    
    devices = get_uisp_devices()
    device_df = devices_to_df(devices, ubiquiti_fields=True)

    df = device_df[device_df['has60GhzRadio']==True]
    # df = df.head(3)

    historys = []
    
    for device_id, device_name in zip(df['id'], df['name']):
        history = get_device_history(device_id, interval)
        
        history['name'] = device_name
        historys.append(history)
    
    if save_filename:
        df.to_csv(save_filename)

    if save_history_filename:
        with open(save_history_filename, 'wb') as pickle_file:
            pickle.dump(historys, pickle_file)

    return historys

def add_down_factor_to_histories(histories):
    histories_new = []
    for history in histories:
        history['down_factor_60ghz'] = get_60_ghz_down_factor(history)
        histories_new.append(history)

    return histories_new

def create_device_timeseries_60ghz_down(history_data):
    datapoints = []
    for transmit_bytes in get_60_ghz_interface(history_data)['transmit']:
        datapoint = {}
        datapoint['timestamp'] = transmit_bytes['x']
        datapoint['has_error'] = transmit_bytes['y']==0
        datapoint['name'] = history_data['name']
 
        datapoints.append(datapoint)
 
    return datapoints

def graph_60ghz_outage_timeseries(pickle_filename):
    with open(pickle_filename, 'rb') as pickle_file:
        histories = pickle.load(pickle_file)

    print(f'Loaded {len(histories)} historys')

    histories = add_down_factor_to_histories(histories)

    # get flat timeseries for all devices
    data_point_lists = []
    for history in histories:
        # if history['down_factor_60ghz'] is not None and history['down_factor_60ghz'] > 0 and history['down_factor_60ghz'] != 1:
        if history['down_factor_60ghz'] is not None and history['down_factor_60ghz'] > 0:
            data_point_lists.append(create_device_timeseries_60ghz_down(history))

    flat_data_point_list = list(itertools.chain.from_iterable(data_point_lists))

    df = pd.DataFrame(flat_data_point_list)

    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['date'] = df['date'].dt.tz_localize('utc').dt.tz_convert('US/Eastern')
    
    df.set_index('date')

    df = df.groupby('name').resample('6T', on='date').sum()
    df = df.reset_index()

    title = f'60Hhz devices approximate down time grouped by time bucket for time ending {date.today()}'

    colorscale = n_colors('rgb(255, 255, 255)', 'rgb(222, 73, 73)', 2, colortype = 'rgb')

    fig = go.Figure(data=go.Heatmap(
        x=df['date'],
        y=df['name'],
        z=df['has_error'],
        colorscale=colorscale,
        showscale=False
    ))

    fig.show()

get_device_histories(save_history_filename='error_factor_day_has60ghz.pkl', save_filename='error_factor_day_has60ghz.csv', interval='day')

# uses pickle file to save data and reduce API requests
graph_60ghz_outage_timeseries('error_factor_day_has60ghz.pkl')