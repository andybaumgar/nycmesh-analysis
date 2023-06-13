import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# NWS Climate Data API endpoint URL
url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'

# Your NWS Climate Data API token
api_token = 'taDwZvMUljBNewOGIIFPlCzFGFtNeimI'

# Query parameters for location, date range, data type, and token
params = {
    'datasetid': 'GSOM',
    'locationid': 'CITY:US360019',
    'startdate': (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d'),
    'enddate': datetime.now().strftime('%Y-%m-%d'),
    'datatypeid': 'PRCP',
    'units': 'standard',
    'limit': 1000,
}

# Headers including the API token
headers = {
    'token': api_token,
}

# Send GET request to the API
response = requests.get(url, params=params, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Extract the date and rainfall values from the API response
    dates = [entry['date'] for entry in data['results']]
    rainfall = [entry['value'] for entry in data['results']]

    # Create a plot using Plotly
    fig = go.Figure(data=go.Scatter(x=dates, y=rainfall, mode='lines+markers'))
    fig.update_layout(title='Rainfall in NYC (Last Day)',
                      xaxis_title='Date',
                      yaxis_title='Rainfall (inches)')

    # Display the plot
    fig.show()

else:
    print('Error occurred while fetching data. Status code:', response.status_code)
