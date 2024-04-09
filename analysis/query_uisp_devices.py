# %%

from uisp_client import devices_to_df, get_uisp_devices, load_uisp_data_from_file

devices = get_uisp_devices()
df = devices_to_df(devices)

df_of_interest = df.query('name.str.contains("155|219")').query(
    'name.str.contains("5916")'
)

print(df_of_interest)
