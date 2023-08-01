def create_map_state_df(df):
    map_df = df[["Latitude", "Longitude", "NN", "nodeName", "Location"]].copy()
    return map_df
