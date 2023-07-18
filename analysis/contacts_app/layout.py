
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from analysis.contacts_app.map import create_map_figure

def create_layout(df, links_df):
    layout = dbc.Container(
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
                                    dbc.Button(
                                        "Clear node",
                                        id="clear-node",
                                        n_clicks=0,
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
                                    dbc.InputGroupText("Node emails", id="node-email-output-label"),
                                    dbc.Textarea(id="node-email-output"),
                                ],
                                style={"padding-bottom": "1em"},
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Nodes", id="node-output-label"),
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
                                figure=create_map_figure(df, links_df),
                                style={"height": "60vh"},
                            ),
                        ],
                        md=7,
                    ),
                ]
            ),
        ],
        fluid=True,
    )

    return layout