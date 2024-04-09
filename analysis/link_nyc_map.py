#%%

import requests
import pandas as pd
from config import meshdb_endpoint
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import os
import plotly.express as px
import plotly.graph_objects as go
# 

# get data folder in parent of current folder
data_folder = Path(__file__).parent.parent/'data'
kiosk_df = pd.read_json(str(data_folder/'kiosks.json'))
node_df = pd.read_json(str(data_folder/'nodes.json'))

kiosk_df['latitude'] = kiosk_df['coordinates'].apply(lambda x: x[1])
kiosk_df['longitude'] = kiosk_df['coordinates'].apply(lambda x: x[0])
node_df['latitude'] = node_df['coordinates'].apply(lambda x: x[1])
node_df['longitude'] = node_df['coordinates'].apply(lambda x: x[0])


# calculate distance

# print(kiosk_df.head())
# print(node_df.head())

# Assuming kiosk_df has columns 'kiosk_id', 'latitude', 'longitude'
# and node_df has columns 'node_id', 'latitude', 'longitude'

# Convert kiosk_df to GeoDataFrame
kiosk_geometry = [Point(xy) for xy in zip(kiosk_df['longitude'], kiosk_df['latitude'])]
kiosk_gdf = gpd.GeoDataFrame(kiosk_df, geometry=kiosk_geometry, crs='EPSG:4326')

# Convert node_df to GeoDataFrame
node_geometry = [Point(xy) for xy in zip(node_df['longitude'], node_df['latitude'])]
node_gdf = gpd.GeoDataFrame(node_df, geometry=node_geometry, crs='EPSG:4326')

# Set coordinate reference system (CRS) if it's not set already
# kiosk_gdf.crs = 'EPSG:4326'
# node_gdf.crs = 'EPSG:4326'

# Buffer nodes with 50m buffer distance
distance_meters = 50
distance_degrees = distance_meters / 111139
node_buffer = node_gdf.geometry.buffer(distance_degrees)

# Check if any kiosks intersect with node buffers
kiosks_within_50m = kiosk_gdf[kiosk_gdf.geometry.intersects(node_buffer.unary_union)]

# Print kiosks within 50m of a node
print("Kiosks within 50m of a node:")
print(kiosks_within_50m)




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
        size=7,
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



# %%
