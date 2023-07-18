
import os
import plotly.express as px

def color_marker(series):
    output_colors = []
    for state in series:
        if state == "selected":
            output_colors.append("orange")
        elif state == "downstream":
            output_colors.append("DodgerBlue")
        else:
            output_colors.append("black")
    return output_colors

def generate_mapbox_scatter_data(df, circle_diameter, color=None):
    if color is None:
        color = color_marker(df["node_state"])
    return {
        "type": "scattermapbox",
        "lat": df["Latitude"],
        "lon": df["Longitude"],
        "mode": "markers",
        "marker": {
            "size": circle_diameter,
            "color": color,
            "symbol": "circle",
            "line": {"color": "white", "width": 5},  # Adjust the outline thickness here
            "opacity": 0.8,
        },
        "text": "NN:"
        + df["NN"].astype(str)
        + "<br>"
        + df["nodeName"]
        + "<br>"
        + df["Location"],
        "showlegend": False,
    }


def generate_mapbox_links(links_df):
    lats = []
    lons = []
    for i, row in links_df.iterrows():
        lats.append(row["to_latitude"])
        lats.append(row["from_latitude"])
        lats.append(None)

        lons.append(row["to_longitude"])
        lons.append(row["from_longitude"])
        lons.append(None)

    trace = px.line_mapbox(lat=lats, lon=lons).data[0]
    trace["line"]["color"] = "rgba(0, 0, 0, .1)"

    return trace


def create_map_figure(df, links_df):
    marker_diameter = 10
    marker_border = 4
    return {
        # need to render two circles since mapbox does not support border
        "data": [
            generate_mapbox_links(links_df),
            generate_mapbox_scatter_data(df, 
                marker_diameter + marker_border, color="white"
            ),
            generate_mapbox_scatter_data(df, marker_diameter),
        ],
        "layout": {
            "mapbox": {
                "accesstoken": os.environ.get("MAPBOX"),
                "style": "carto-positron",
                "center": {"lat": 40.7128, "lon": -74.0060},
                "zoom": 10,
            },
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        },
    }