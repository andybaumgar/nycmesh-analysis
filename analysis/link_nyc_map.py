# %%

import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import plotly.graph_objects as go
import pickle

data_small_folder = Path(__file__).parent.parent / "data_small"
data_folder = Path(__file__).parent.parent / "data"


def get_nodes_near_kiosks():
    kiosk_df = pd.read_json(str(data_small_folder / "kiosks.json"))
    node_df = pd.read_json(str(data_small_folder / "nodes.json"))

    node_df = node_df[node_df["status"] != "Installed"]

    kiosk_df["latitude"] = kiosk_df["coordinates"].apply(lambda x: x[1])
    kiosk_df["longitude"] = kiosk_df["coordinates"].apply(lambda x: x[0])
    node_df["latitude"] = node_df["coordinates"].apply(lambda x: x[1])
    node_df["longitude"] = node_df["coordinates"].apply(lambda x: x[0])

    kiosk_geometry = [
        Point(xy) for xy in zip(kiosk_df["longitude"], kiosk_df["latitude"])
    ]
    kiosk_gdf = gpd.GeoDataFrame(kiosk_df, geometry=kiosk_geometry, crs="EPSG:4326")

    node_geometry = [Point(xy) for xy in zip(node_df["longitude"], node_df["latitude"])]
    node_gdf = gpd.GeoDataFrame(node_df, geometry=node_geometry, crs="EPSG:4326")

    distance_meters = 50
    distance_degrees = distance_meters / 111139
    kiosk_buffer = kiosk_gdf.geometry.buffer(distance_degrees)

    nodes_near_kiosks = node_gdf[node_gdf.geometry.intersects(kiosk_buffer.unary_union)]

    print('non-"Installed" Nodes within 50m of a kiosk:')
    print(nodes_near_kiosks)

    data = {
        "nodes_near_kiosks": nodes_near_kiosks,
        "kiosk_df": kiosk_df,
        "node_df": node_df,
    }

    with open(data_folder / "nodes_near_kiosks.pkl", "wb") as f:
        pickle.dump(data, f)

    return nodes_near_kiosks, kiosk_df, node_df


def map_nodes_near_kiosks(nodes_near_kiosks, kiosk_df, node_df):

    fig = go.Figure(go.Scattermapbox())

    fig.add_trace(
        go.Scattermapbox(
            mode="markers",
            lon=node_df["longitude"],
            lat=node_df["latitude"],
            marker=dict(
                size=10,
                color="blue",
            ),
            name="Nodes",
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            mode="markers",
            lon=kiosk_df["longitude"],
            lat=kiosk_df["latitude"],
            marker=dict(
                size=10,
                color="brown",
            ),
            name="Kiosks",
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            mode="markers",
            lon=nodes_near_kiosks["longitude"],
            lat=nodes_near_kiosks["latitude"],
            marker=dict(
                size=7,
                color="yellow",
            ),
            name="Nodes within 50m of a kiosk",
        )
    )

    fig.update_layout(
        hovermode="closest",
        mapbox=dict(
            style="carto-positron",
            center=dict(
                lon=node_df["longitude"].mean(), lat=node_df["latitude"].mean()
            ),
            zoom=10,
        ),
    )

    fig.update_layout(title_text="Uninstalled Nodes within 50m of a kiosk")

    fig.write_html(str(data_folder / "nodes_near_kiosks.html"))

    fig.show()


def get_data_from_file():
    with open(data_folder / "nodes_near_kiosks.pkl", "rb") as f:
        data = pickle.load(f)
        nodes_near_kiosks = data["nodes_near_kiosks"]
        kiosk_df = data["kiosk_df"]
        node_df = data["node_df"]
    return nodes_near_kiosks, kiosk_df, node_df


# nodes_near_kiosks, kiosk_df, node_df = get_nodes_near_kiosks()

nodes_near_kiosks, kiosk_df, node_df = get_data_from_file()

map_nodes_near_kiosks(nodes_near_kiosks, kiosk_df, node_df)

# %%
