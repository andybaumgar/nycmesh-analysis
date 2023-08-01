from pathlib import Path
import re
import mesh_database_client 
import networkx as nx

def get_data_file_path(data_filename):
    data_path_object = Path(__file__).parent.parent / 'data'
    data_file_path =  str(data_path_object / data_filename)
    return data_file_path

def get_distance_miles(location_1, location_2):
    x1 = location_1['Latitude']
    y1 = location_1['Longitude']
    x2 = location_2['Latitude']
    y2 = location_2['Longitude']

    distance_degrees = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    approximate_distance_miles = distance_degrees * 69

    return approximate_distance_miles

def nns_from_string(input_string):
    matches = re.findall("(\d{3,})", input_string)

    if not matches or len(matches) <= 1:
        return None
    else:
        matches = [int(match) for match in matches]
        return matches[0], matches[1]

