#%%
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import plotly.express as px
import datetime as dt

import mesh_database_client


load_dotenv() 
spreadsheet_id = os.environ.get("SPREADSHEET_ID")

database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)
df = database_client.signup_df

title = f'NYC Mesh Nodes'

px.set_mapbox_access_token(os.environ.get('MAPBOX'))

fig = px.scatter_mapbox(
    df, 
    lat="Latitude", 
    lon="Longitude",   
    zoom=11.8, 
    title=title,
    center={"lat":40.693302,"lon":-73.974665}
    )

fig.update_traces(marker=dict(
    size=6,
    opacity=0.5,
    ),
    selector=dict(mode='markers'))

fig.show()
# %%


# Create a base Mapbox figure
fig = go.Figure(go.Scattermapbox())

# Add nodes to the figure
fig.add_trace(go.Scattermapbox(
    mode='markers',
    lon=node_df['longitude'],
    lat=node_df['latitude'],
    marker=dict(
        size=10,
        color='blue',
    ),
    name='Nodes'
))

# Add original kiosks to the figure
fig.add_trace(go.Scattermapbox(
    mode='markers',
    lon=kiosk_df['longitude'],
    lat=kiosk_df['latitude'],
    marker=dict(
        size=10,
        color='brown',
    ),
    name='Original Kiosks'
))

# Add found kiosks within 50m of a node to the figure
fig.add_trace(go.Scattermapbox(
    mode='markers',
    lon=kiosks_within_50m['longitude'],
    lat=kiosks_within_50m['latitude'],
    marker=dict(
        size=10,
        color='yellow',
    ),
    name='Kiosks within 50m of a Node'
))

# Update layout to set Mapbox parameters
fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        style="carto-positron",
        center=dict(lon=node_df['longitude'].mean(), lat=node_df['latitude'].mean()),
        zoom=10
    )
)

# Show the figure
fig.show()
