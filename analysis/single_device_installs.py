#%%
import os
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.express as px

import mesh_database_client
from uisp_client import load_uisp_data_from_file, devices_to_df

# setup 

load_dotenv()

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

px.set_mapbox_access_token(os.environ.get('MAPBOX'))

# get devices

# devices = get_uisp_devices(save_filename="sxt_test.json")
device_name_part = 'lbe'
devices = load_uisp_data_from_file("sxt_test.json")
df = devices_to_df(devices)
nn_count = df['nn'].value_counts()
single_device_nns = list(nn_count[nn_count==1].index)
print(486 in single_device_nns)
single_devices_df = df[df['nn'].isin(single_device_nns)]

single_devices_sxt = single_devices_df[single_devices_df['name'].str.contains(device_name_part, case=False)]
print(single_devices_sxt)
print(single_devices_sxt.shape[0])


# map (uses spreadsheet columns)

single_sxt_nns = list(single_devices_sxt['nn'])
install_sheet_single_sxt = database_client.signup_df[database_client.signup_df['NN'].isin(single_sxt_nns)]

fig = px.scatter_mapbox(
    install_sheet_single_sxt, 
    lat="Latitude", 
    lon="Longitude",   
    title=f"Single Device Installs Containing '{device_name_part}'",
    hover_name="NN",
    hover_data=['notes', 'notes2'],
    )

fig.show()