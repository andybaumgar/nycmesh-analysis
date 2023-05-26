#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
from datetime import date

from analysis.uisp_client import load_uisp_data_from_file, devices_to_df, get_device_history, get_uisp_devices


devices = load_uisp_data_from_file("uisp_output_20230522.json")
df = devices_to_df(devices, ubiquiti_fields=True)
df = df.drop_duplicates(subset='nn', keep="first")

df = df['site_name'].value_counts().sort_index().reset_index()
df=df.sort_values(by='site_name', ascending=False)
# df=df.head(20)
df['subscriptions_$'] = df['site_name']*20

# fig = px.bar(df, x='index', y="subscriptions_$", title=f"Top 20 Sites - Approximate Subscriptions as of {date.today()}")
fig = px.bar(df, x='index', y="site_name", title=f"Top 20 Sites - as of {date.today()}")
fig.show()