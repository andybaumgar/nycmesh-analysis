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

import mesh_database_client

data_path_object = Path(__file__).parent.parent / 'data'

df_1 = pd.read_csv(str(data_path_object / '20230115.csv'))
df_2 = pd.read_csv(str(data_path_object / '20230119.csv'))

signal_1=df_1['signal'].mean()
signal_2=df_2['signal'].mean()

signal_difference = signal_1-signal_2

# df_compare = pd.concat([df_1.set_index('name'),df_2.set_index('name')], axis=1, join='inner').reset_index()
df_compare = df_1.merge(df_2, on='name', how='inner', suffixes=('_1', '_2'))

df_compare['signal_difference'] = df_compare["signal_2"] - df_compare["signal_1"]

print("")
# fig = px.bar(df_compare, x='name', y=['signal_1', 'signal_2'], barmode='group')
title = f'Vernon Connected LBE Signal Strength Difference<br><sup>(negative values indecate worsening signal)</sup>'
fig = px.bar(df_compare, x='name', y='signal_difference', title=title)

# fig.update_yaxes(autorange="reversed")
fig.show()