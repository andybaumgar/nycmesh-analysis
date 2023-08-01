from math import sqrt


def nn_to_latitude(nn, database_client):
    try:
        return database_client.nn_to_location(nn)["Latitude"]
    except:
        return None


def nn_to_longitude(nn, database_client):
    try:
        return database_client.nn_to_location(nn)["Longitude"]
    except:
        return None


def get_distance_miles(location1, location2):
    lat1 = location1["Latitude"]
    lon1 = location1["Longitude"]
    lat2 = location2["Latitude"]
    lon2 = location2["Longitude"]

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    distance_deg = sqrt(dlat**2 + dlon**2)
    deg_to_feet = 288200
    feet_to_miles = 5280
    distance_miles = distance_deg * deg_to_feet / feet_to_miles

    return distance_miles


def get_link_distance(nn_1: int, nn_2: int, database_client):
    location_1 = database_client.nn_to_location(nn_1)
    location_2 = database_client.nn_to_location(nn_2)

    distance_miles = get_distance_miles(location_1, location_2)

    return distance_miles
