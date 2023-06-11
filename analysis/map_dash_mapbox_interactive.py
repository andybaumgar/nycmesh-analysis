import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash import ctx
import os
import pandas as pd
import plotly.express as px

from dotenv import load_dotenv
load_dotenv() 

import mesh_database_client

app = dash.Dash(__name__)

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)
df = database_client.signup_df
df = df[df['NN'] != 0]
df['NN'] = df['NN'].astype(str)

# Sample DataFrame
# df = pd.DataFrame({
#     'City': ['New York', 'London', 'Paris', 'Tokyo'],
#     'Latitude': [40.7128, 51.5074, 48.8566, 35.6895],
#     'Longitude': [-74.0060, -0.1278, 2.3522, 139.6917]
# })

def create_figure(bearing):
    return {
        'data': [{
            'type': 'scattermapbox',
            'lat': df['Latitude'],
            'lon': df['Longitude'],
            'mode': 'markers',
            'marker': {'size': 8},
            'text': df['NN'] + "<br>" + df['nodeName'] + "<br>" + df['Location'],
        }],
        'layout': {
            'mapbox': {
                'accesstoken': os.environ.get('MAPBOX'),
                'style': 'mapbox://styles/mapbox/streets-v11',
                'center': {'lat': 40.7128, 'lon': -74.0060},
                'zoom': 10,
                'pitch': 120,
                'bearing': bearing
            },
            'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
        }
    }
    # return px.scatter_mapbox(
    #         df,
    #         lat='Latitude',
    #         lon='Longitude',
    #         hover_name='City',
    #         zoom=3
    #     )

app.layout = html.Div([
    dcc.Graph(
        id='map',
        figure=create_figure(10)
    ),
    html.Button('Roate Left', id='rotate-left', n_clicks=0),
    html.Button('Roate Right', id='rotate-right', n_clicks=0),
])

# @app.callback(Output('click-output', 'children'), [Input('map', 'clickData')])
# def display_click_data(clickData):
#     if clickData is not None:
#         lat = clickData['points'][0]['lat']
#         lon = clickData['points'][0]['lon']
#         return f'Clicked location coordinates: Latitude={lat}, Longitude={lon}'
#     else:
#         return 'Click on the map to retrieve coordinates.'
    

@app.callback(
        Output('map', 'figure'),
    [
        Input('rotate-right', 'n_clicks'), 
        Input('rotate-left', 'n_clicks'), 
    ],
        State('map', 'figure'))
        
def update_output(right_clicks, left_clicks, current_figure):
    button_clicked = ctx.triggered_id

    current_bearing_value = current_figure['layout']['mapbox']['bearing']
    if button_clicked == 'rotate-right':
        new_bearing_value = current_bearing_value - 10
    else:
        new_bearing_value = current_bearing_value + 10

    new_figure = current_figure.copy()
    new_figure['layout']['mapbox']['bearing'] = new_bearing_value

    return new_figure

if __name__ == '__main__':
    app.run_server(debug=True)
