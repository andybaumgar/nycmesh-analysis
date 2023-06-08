from jupyter_dash import JupyterDash
import json
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import dash_daq as daq
from dash.dependencies import Output, Input
import os
from dotenv import load_dotenv
load_dotenv() 

MAP_ID = "map-id"
COORDINATE_CLICK_ID = "coordinate-click-id"

# linked stylesheet
app = JupyterDash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Create layout.
app.layout = html.Div([
    html.H1("Example: Gettings coordinates from click"),
    
    # map component
    dl.Map(id=MAP_ID, style={'width': '1000px', 'height': '500px'}, center=[32.7, -96.8], zoom=5, children=[
        dl.TileLayer(url=f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={os.environ.get("MAPBOX")}')
        ]),
    html.P("Coordinate (click on map):"),
    
    # map output div
    html.Div(id=COORDINATE_CLICK_ID),

    # color picker component
    daq.ColorPicker(
        id='my-color-picker-1',
        label='Color Picker',
        value=dict(hex='#119DFF')
    ),

    # color picker output div
    html.Div(id='color-picker-output-1')

])

# map component event bound to input, output div bound to output 
@app.callback(Output(COORDINATE_CLICK_ID, 'children'),
              [Input(MAP_ID, 'click_lat_lng')])
def click_coord(e):
    if e is not None:
        # return value is entered into output div
        return json.dumps(e)
    else:
        return "-"

# color picker component event bound to input, output div bound to output
@app.callback(
    Output('color-picker-output-1', 'children'),
    Input('my-color-picker-1', 'value')
)
def update_output(value):
    # return value is entered into output div
    return f'The selected color is {value}.'

# app.run_server(host='127.0.0.1', port=8081, debug=True) 
app.run_server(host='127.0.0.1', port=8080, debug=True, mode='inline')