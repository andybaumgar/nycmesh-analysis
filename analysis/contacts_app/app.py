import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

import mesh_database_client

from analysis.contacts import nns_to_emails
from analysis.contacts_app.database_utils import create_map_state_df
from analysis.contacts_app.layout import create_layout
from analysis.contacts_app.map import color_marker
from analysis.mesh_utils import get_links_df_with_locations
from analysis.node_graph import NYCMeshGraph

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
# application = app.server
app.title = "Hub Contact Finder"

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(
    spreadsheet_id=spreadsheet_id, include_active=True
)
links_df = get_links_df_with_locations(database_client)

df_emails = database_client.active_node_df
df = create_map_state_df(df_emails)
df["node_state"] = "deselected"

empty_node_text = "No node selected"

# shortest_paths, active_nns = create_shortest_path_graph(database_client)
# graph = NYCMeshGraph(links_df)
graph = NYCMeshGraph(links_df)


app.layout = create_layout(df, links_df)


@app.callback(
    [
        Output("nn-input", "value", allow_duplicate=True),
        Output("map", "figure", allow_duplicate=True),
        Output("install-sheet-df", "data", allow_duplicate=True),
        Output("node-email-output", "value", allow_duplicate=True),
        Output("node-output", "value", allow_duplicate=True),
        Output("node-output-label", "children", allow_duplicate=True),
        Output("node-email-output-label", "children", allow_duplicate=True),
        Output("loading-output", "children", allow_duplicate=True),
    ],
    [Input("clear-node", "n_clicks")],
    [State("map", "figure"), State("install-sheet-df", "data")],
    prevent_initial_call=True,
)
def deselect_node(n_clicks, current_figure, df_data):
    new_figure = current_figure.copy()
    new_figure["data"][-1]["marker"]["color"] = color_marker(df["node_state"])

    return None, new_figure, df.to_dict("records"), "", "", "Nodes", "Node emails", ""


@app.callback(
    [
        Output("nn-input", "value", allow_duplicate=True),
        Output("map", "figure", allow_duplicate=True),
        Output("install-sheet-df", "data", allow_duplicate=True),
        Output("node-email-output", "value", allow_duplicate=True),
        Output("node-output", "value", allow_duplicate=True),
        Output("node-output-label", "children", allow_duplicate=True),
        Output("node-email-output-label", "children", allow_duplicate=True),
        Output("loading-output", "children", allow_duplicate=True),
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
def select_node(
    click_data, select_node_clicks, current_figure, df_data, nn_input, password
):
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

    downstream_nns = graph.get_dependent_nodes(selected_nn)

    downstream_nns_string = ", ".join([str(nn) for nn in downstream_nns])

    downstream_nns_emails = nns_to_emails(
        (downstream_nns + [selected_nn]), database_client, paste_format=False
    )
    if password == os.environ.get("MEMBER_EMAIL_PASSWORD"):
        downstream_nns_emails_output = downstream_nns_emails
    else:
        downstream_nns_emails_output = ""

    # change downstream node state
    new_df.loc[new_df["NN"].isin(downstream_nns), "node_state"] = "downstream"

    # update map
    new_figure["data"][-1]["marker"]["color"] = color_marker(new_df["node_state"])

    node_label_text = "Nodes"
    if downstream_nns:
        node_label_text = f"Nodes ({len(downstream_nns)})"

    node_emails_label_text = "Node emails"
    if downstream_nns_emails:
        node_emails_label_text = f"Node emails ({len(downstream_nns_emails)})"

    return (
        row["NN"],
        new_figure,
        new_df.to_dict("records"),
        downstream_nns_emails_output,
        downstream_nns_string,
        node_label_text,
        node_emails_label_text,
        "",
    )


if __name__ == "__main__":
    if os.environ.get("ENV") == "development":
        app.run_server(debug=True)
    else:
        app.run_server(debug=False)
