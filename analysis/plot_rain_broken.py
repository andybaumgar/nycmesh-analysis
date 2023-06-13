import requests
import plotly.graph_objects as go

# API endpoint URL
url = 'https://api.weather.gov/gridpoints/OKX/33,34/forecast/hourly'

# Send GET request to the API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Extract the hourly precipitation values from the API response
    
    hourly_precipitation = [hour['probabilityOfPrecipitation']['value']
                            for hour in data['properties']['periods']]

    # Create a list of datetime values for the x-axis
    datetime_values = [hour['startTime'] for hour in data['properties']['periods']]

    # Create a plot using Plotly
    fig = go.Figure(data=go.Scatter(x=datetime_values, y=hourly_precipitation))
    fig.update_layout(title='Hourly Precipitation for NYC',
                      xaxis_title='Date and Time',
                      yaxis_title='Precipitation (inches)')

    # Display the plot
    fig.show()

else:
    print('Error occurred while fetching data. Status code:', response.status_code)
