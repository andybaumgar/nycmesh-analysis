import humanize
import datetime as dt

def human_timedelta(time):
    return humanize.precisedelta(time - dt.datetime.now(dt.timezone.utc), suppress=["seconds", "minutes", "days"])

def hours_delta(time):
    delta = dt.datetime.now(dt.timezone.utc) - time
    hours = delta.total_seconds()/3600
    hours = round(hours, 1)
    return hours