import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.dash import no_update
import dash_daq as daq
from dash import ctx
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dotenv import load_dotenv

load_dotenv()

import mesh_database_client
from mesh_utils import (
    get_downstream_nns,
    create_shortest_path_graph,
    get_links_df_with_locations,
)
from contacts import nns_to_emails

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)
links_df = get_links_df_with_locations(database_client)
df = database_client.signup_df
df = df[df["NN"] != 0]
df["nn_string"] = df["NN"].astype(str)
df["node_state"] = "deselected"

empty_node_text = "No node selected"

shortest_paths, active_nns = create_shortest_path_graph(database_client)


def color_marker(series):
    output_colors = []
    for state in series:
        if state == "selected":
            output_colors.append("orange")
        elif state == "downstream":
            output_colors.append("DodgerBlue")
        else:
            output_colors.append("gray")
    return output_colors


def generate_mapbox_scatter_data(circle_diameter, color=None):
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
        + df["nn_string"]
        + "<br>"
        + df["nodeName"]
        + "<br>"
        + df["Location"],
        "showlegend": False,
    }


def generate_mapbox_links():
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


def create_map_figure():
    marker_diameter = 10
    marker_border = 4
    return {
        # need to render two circles since mapbox does not support border
        "data": [
            generate_mapbox_links(),
            generate_mapbox_scatter_data(
                marker_diameter + marker_border, color="white"
            ),
            generate_mapbox_scatter_data(marker_diameter),
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


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.NavbarSimple(
                    children=[
                        dbc.NavItem(
                            dbc.NavLink(
                                "GitHub",
                                href="https://github.com/andybaumgar/nycmesh-analysis/blob/main/analysis/contacts_app.py",
                            )
                        ),
                    ],
                    brand="Hub Contact Finder",
                    brand_href="#",
                    color="dark",
                    dark=True,
                )
            ],
            style={"padding-bottom": "20px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("NN Input"),
                                dbc.Input(id="nn-input", type="number"),
                                dbc.Button(
                                    "Select node", id="select-node-button", n_clicks=0
                                ),
                            ],
                            style={"padding-bottom": "1em"},
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Password"),
                                dbc.Input(
                                    id="password",
                                    type="password",
                                    placeholder="Enter password to view member emails",
                                ),
                            ],
                            style={"padding-bottom": "1em"},
                        ),
                        dcc.Store(id="install-sheet-df", data=df.to_dict("records")),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Node emails"),
                                dbc.Textarea(id="node-email-output"),
                            ],
                            style={"padding-bottom": "1em"},
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Nodes"),
                                dbc.Textarea(id="node-output"),
                            ],
                            style={"padding-bottom": "1em"},
                        ),
                    ],
                    md=5,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="map",
                            figure=create_map_figure(),
                            style={"height": "60vh"},
                        ),
                        dbc.Button(
                            "Deselect node",
                            id="regenerate-links",
                            n_clicks=0,
                            style={"margin-top": ".5em"},
                        ),
                    ],
                    md=7,
                ),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    [
        Output("nn-input", "value", allow_duplicate=True),
        Output("map", "figure", allow_duplicate=True),
        Output("install-sheet-df", "data", allow_duplicate=True),
        Output("node-email-output", "value", allow_duplicate=True),
        Output("node-output", "value", allow_duplicate=True),
    ],
    [Input("regenerate-links", "n_clicks")],
    [State("map", "figure"), State("install-sheet-df", "data")],
    prevent_initial_call=True,
)
def deselect_node(n_clicks, current_figure, df_data):
    new_figure = current_figure.copy()
    new_figure["data"][-1]["marker"]["color"] = color_marker(df["node_state"])

    return None, new_figure, df.to_dict("records"), "", ""


@app.callback(
    [
        Output("nn-input", "value", allow_duplicate=True),
        Output("map", "figure", allow_duplicate=True),
        Output("install-sheet-df", "data", allow_duplicate=True),
        Output("node-email-output", "value", allow_duplicate=True),
        Output("node-output", "value", allow_duplicate=True),
    ],
    [Input("map", "clickData"), Input("select-node-button", "n_clicks")],
    [
        State("map", "figure"),
        State("install-sheet-df", "data"),
        State("nn-input", "value"),
        State("password", "value"),
    ],
    prevent_initial_call=True,
)
def select_node(click_data, select_node_clicks, current_figure, df_data, nn_input, password):
    print(click_data)

    selected_nn = None

    new_figure = current_figure.copy()
    new_figure["data"][-1]["marker"]["color"] = color_marker(df["node_state"])

    new_df = pd.DataFrame.from_dict(df_data)
    new_df["node_state"] = "unselected"

    if click_data is not None:
        point = click_data["points"][0]
        selected_nn = new_df.loc[
            (new_df["Latitude"] == point["lat"]) & (new_df["Longitude"] == point["lon"])
        ].iloc[0]["NN"]
    else:
        selected_nn = nn_input

    selected_index = new_df.loc[new_df["NN"] == selected_nn].index[0]
    row = new_df.iloc[selected_index]
    row["node_state"] = "selected"
    new_df.iloc[selected_index] = row

    downstream_nns = get_downstream_nns(
        selected_nn, database_client, shortest_paths, active_nns
    )
    downstream_nns_string = ", ".join([str(nn) for nn in downstream_nns])

    if password == os.environ.get("MEMBER_EMAIL_PASSWORD"):
        downstream_nns_emails = nns_to_emails(downstream_nns, database_client)
    else:
        downstream_nns_emails = ''

    # change downstream node state
    new_df.loc[new_df["NN"].isin(downstream_nns), "node_state"] = "downstream"

    # update map
    new_figure["data"][-1]["marker"]["color"] = color_marker(new_df["node_state"])

    return (
        row["NN"],
        new_figure,
        new_df.to_dict("records"),
        downstream_nns_emails,
        downstream_nns_string,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(debug=False)
