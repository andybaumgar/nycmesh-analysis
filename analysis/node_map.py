#%%
import os
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.express as px
import os
import re
from dotenv import load_dotenv
import plotly.express as px
import humanize
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
