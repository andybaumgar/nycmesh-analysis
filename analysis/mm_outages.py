from influxdb import InfluxDBClient
import pandas as pd
from pathlib import Path
import plotly.express as px
import os
from dotenv import load_dotenv
import numpy as np
import scipy.stats as stats

from mesh_utils import get_nns_from_string
from map_utils import get_link_distance
import mesh_database_client

load_dotenv()


def get_mm_data_from_database_and_save(num_days=1):
    client = InfluxDBClient(host="10.70.178.21", port=8086)
    client.switch_database("monitoring")

    query = f'SELECT * FROM "devices" WHERE time > now() - {num_days}d'
    result = client.query(query)

    df = pd.DataFrame(result.get_points())
    data_dir = Path(__file__).parent.parent / "data"
    output_path = str(data_dir / f"60ghz_devices_{num_days}d.csv")
    df.to_csv(output_path)

    return df, output_path


def add_nns(df):
    df["to"] = df["name"].apply(lambda x: get_nns_from_string(x, 0))
    df["from"] = df["name"].apply(lambda x: get_nns_from_string(x, 1))

    return df


def add_distance(df):
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)
    df = df[df["to"].notna() & df["from"].notna()]
    df["to"] = df["to"].astype(int)
    df["from"] = df["from"].astype(int)

    for index, row in df.iterrows():
        df.loc[index, "distance"] = get_link_distance(
            row["to"], row["from"], database_client
        )

    return df


def get_mm_data_from_file(data_filename):
    data_dir = Path(__file__).parent.parent / "data"
    data_file_path = str(data_dir / data_filename)
    df = pd.read_csv(data_file_path)
    return df


def group_and_populate_df(df, outlire_cutoff_outage=None, outlire_cutoff_distance=None):
    # aggrigate sum of outages by device name
    df = df.groupby(["name"]).sum()
    df = df.reset_index()
    df = df.sort_values(by=["outage"], ascending=False)

    df = df[df["outage"] < outlire_cutoff_outage]

    # set outage to .001 if outage is 0 so it is visible on log scale
    df["outage"] = df["outage"].apply(lambda x: 0.01 if x == 0 else x)

    df = add_nns(df)
    df = add_distance(df)

    df = df[df["distance"] < outlire_cutoff_distance]

    return df


def plot_mm_data_overview(df):
    df = group_and_populate_df(
        df, outlire_cutoff_outage=1440, outlire_cutoff_distance=4
    )

    fig = px.bar(
        df,
        x="name",
        y="outage",
        color="outage",
        # color_continuous_scale="sunset",
        log_y=True,
    )
    # add labels to axies and title
    fig.update_layout(
        title="60Ghz devices approximate down time for last 21 days <br><i>(devices with more than 1 day of outage are not shown)</i>",
        xaxis_title="Device Name",
        yaxis_title="Approximate Minutes of Outage <br><i>(log scale)</i>",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.show()

    print(df)


def improve_text_position(x):
    """it is more efficient if the x values are sorted"""
    # fix indentation
    positions = ["top center", "bottom center"]  # you can add more: left center ...
    return [positions[i % len(positions)] for i in range(len(x))]


def add_type(df):
    df["type"] = df["name"].apply(lambda x: x.split("-")[2])
    return df


def plot_outage_distance_correlation(df):
    outlire_cutoff_outage = 50
    outlire_cutoff_distance = 4
    df = group_and_populate_df(
        df,
        outlire_cutoff_outage=outlire_cutoff_outage,
        outlire_cutoff_distance=outlire_cutoff_distance,
    )
    df = add_type(df)
    df["display-name"] = df["name"].apply(lambda x: x.replace("nycmesh-", ""))
    df = df.sort_values(by=["distance"], ascending=True)

    # df = df[df["name"].str.contains("af60lr")]

    y_data_processed = df["outage"]
    y_data_processed = np.log(y_data_processed)

    # slope, intercept, r_value, p_value, std_err = stats.linregress(
    #     df["distance"], log_y_data
    # )
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df["distance"].to_numpy(), y_data_processed
    )
    best_fit_line = slope * df["distance"] + intercept
    r_squared = r_value**2

    best_fit_line = np.exp(best_fit_line)

    fig = px.scatter(
        df,
        x="distance",
        y="outage",
        color="type",
        # color_continuous_scale="sunset",
        log_y=True,
        text="display-name",
    )
    # add labels to axies and title
    fig.update_layout(
        title=f"60Ghz devices approximate down time for last 30 days <br><i>(devices with more than {outlire_cutoff_outage} minutes of outage and {outlire_cutoff_distance} miles of distance are not shown)<br>R-Squared={r_squared}</i> ",
        xaxis_title="Distance between devices (miles)",
        yaxis_title="Approximate Minutes of Outage <br><i>(log scale)</i>",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(
        marker=dict(size=12),
    )
    fig.update_traces(textposition="bottom right")
    fig.update_traces(textposition=improve_text_position(df["distance"]))

    fig.add_trace(px.line(x=df["distance"], y=best_fit_line).data[0])
    # fig.update_layout(
    #     annotations=[dict(x=0.5, y=0.9, showarrow=False, text=f"R² = {r_squared:.2f}")]
    # )
    fig.show()

    print(df)


# df, output_path = get_mm_data_from_database_and_save(num_days=30)
# print(f"Saved data to {output_path}")

df = get_mm_data_from_file("60ghz_devices_30d.csv")
plot_outage_distance_correlation(df)
