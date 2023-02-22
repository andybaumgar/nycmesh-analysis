import humanize
import datetime as dt
import os
from pathlib import Path

def human_timedelta(time):
    return humanize.precisedelta(time - dt.datetime.now(dt.timezone.utc), suppress=["seconds", "minutes", "days"])

def hours_delta(time):
    delta = dt.datetime.now(dt.timezone.utc) - time
    hours = delta.total_seconds()/3600
    hours = round(hours, 1)
    return hours

def save_plotly_fig_to_directory(fig, directory_name):
    html_path_object = Path(__file__).parent.parent / 'output' / f'{directory_name}'
    try:
        os.mkdir(html_path_object)
    except Exception as e:
        pass
    html_path =  str(html_path_object / f'index.html')
    fig.write_html(html_path,
                full_html=False,
                include_plotlyjs='cdn')