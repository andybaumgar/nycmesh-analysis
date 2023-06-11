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
import random
import string

MAP_ID = "map-id"
COORDINATE_CLICK_ID = "coordinate-click-id"

# linked stylesheet
app = JupyterDash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

def create_link(src):
    id =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return html.Iframe(id=id, src=src,
                style={"height": "1067px", "width": "100%"})

# Create layout.
app.layout = html.Div([
    html.H1("Example: Gettings coordinates from click"),
    
    # map component
    dl.Map(id=MAP_ID, style={'width': '1000px', 'height': '500px'}, center=[32.7, -96.8], zoom=5, maxZoom=30, children=[
        dl.TileLayer(url=f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={os.environ.get("MAPBOX")}')
        ]),
    html.P("Coordinate (click on map):"),
    
    # map output div
    html.Div(id=COORDINATE_CLICK_ID),
    html.A("Google Maps Link", id='google-maps-link', href='https://nycmesh.net/', target="_blank"),

])

def map_json_to_google_map_url(coordinates_list):
    return f"https://www.google.com/maps/search/?api=1&query={coordinates_list[0]},{coordinates_list[1]}"

# map component event bound to input, output div bound to output 
@app.callback([Output(COORDINATE_CLICK_ID, 'children'), Output('google-maps-link', 'href')],
    [Input(MAP_ID, 'click_lat_lng')])
def click_coord(e):
    if e is not None:
        google_map_url = map_json_to_google_map_url(e) 
        # return value is entered into output div
        return (google_map_url, google_map_url)
        # return json.dumps(e)
    else:
        return ("-", "-")

# app.run_server(host='127.0.0.1', port=8081, debug=True) 
app.run_server(host='127.0.0.1', port=8080, debug=True, mode='inline')