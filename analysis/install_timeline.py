#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd

import mesh_database_client
from uisp_client import load_uisp_data_from_file, devices_to_df

# setup 

load_dotenv()

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

px.set_mapbox_access_token(os.environ.get('MAPBOX'))


signup_df = database_client.signup_df
signup_df = signup_df[signup_df['NN'] > 0]
signup_df = signup_df[signup_df['Status'].isin(['Installed', 'Abandoned', 'Unsubscribe', 'Powered Off'])]

signup_df['timestamp_start'] = pd.to_datetime(signup_df['Timestamp'])
signup_df['timestamp_end'] = signup_df['timestamp_start'] + pd.Timedelta(days=20)

# df['Open'] = pd.to_datetime(df['OPEN TIME'],format= '%H:%M:%S' ).dt.time

print(signup_df)
print(signup_df.columns)

fig = px.timeline(
    signup_df, 
    x_start="timestamp_start", 
    x_end="timestamp_end", 
    y="Status", 
    # y="Neighborhood", 
    hover_data=['NN', 'notes', 'notes2'],
    # color='Status',
    # color='Neighborhood',
    color_discrete_sequence=['rgba(147,112,219,0.05)']
    # height=400, 
    # width=1000, 
)
fig.show()
# %%
