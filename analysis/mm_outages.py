from influxdb import InfluxDBClient
import pandas as pd
from pathlib import Path
import plotly.express as px

from utils import get_data_file_path

def get_mm_data_from_database_and_save(num_days=1):
    client = InfluxDBClient(host='10.70.178.21', port=8086)
    client.switch_database('monitoring')

    query = f'SELECT * FROM "devices" WHERE time > now() - {num_days}d'
    result = client.query(query)

    df = pd.DataFrame(result.get_points())
    data_dir = Path(__file__).parent.parent / 'data'
    output_path = str(data_dir / f'60ghz_devices_{num_days}d.csv')
    df.to_csv(output_path)

    return df, output_path

def get_mm_data_from_file(data_filename):
    data_dir = Path(__file__).parent.parent / 'data'
    data_file_path =  str(data_dir / data_filename)
    df = pd.read_csv(data_file_path)
    return df

def analyze_and_plot_mm_data(df):
    # aggrigate sum of outages by device name
    df = df.groupby(['name']).sum()
    df = df.reset_index()
    df = df.sort_values(by=['outage'], ascending=False)

    one_day_in_minutes = 1440
    df = df[df['outage'] < one_day_in_minutes]
    df = df[df['outage'] > 0]

    fig = px.bar(df, x='name', y='outage', color='outage', color_continuous_scale='sunset', log_y=True)
    # add labels to axies and title
    fig.update_layout( 
        title='60Ghz devices approximate down time for last 21 days <br><i>(devices with more than 1 day of outage are not shown)</i>',
        xaxis_title='Device Name',
        yaxis_title='Approximate Minutes of Outage <br><i>(log scale)</i>'
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.show()
    
    print(df) 

# df, output_path = get_mm_data_from_database(num_days=21)
# print(f'Saved data to {output_path}')

df = get_mm_data_from_file('60ghz_devices_21d.csv')
analyze_and_plot_mm_data(df)