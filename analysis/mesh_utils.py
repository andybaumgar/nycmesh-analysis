import re
import mesh_database_client
from utils import nn_to_latitude, nn_to_longitude
import networkx as nx
import os

def nn_from_string(input_string):
    matches = re.findall("(\d{3,})", input_string)
    if not matches:
        return None

    return int(re.findall("(\d{3,})", input_string)[0])


def nn_to_ip(nn):
    ip_fourth_octet=nn%100
    ip_third_octet=int((nn-ip_fourth_octet)/100)
    ip = f"10.69.{ip_third_octet}.{ip_fourth_octet}"
    return ip

def get_clean_link_df(database_client):
    links_df = database_client.links_df.copy()
    links_df = links_df[links_df['status'] != 'dead']
    # convert IN to NN
    for field in ['to', 'from']:
        links_df[field] = links_df[field].apply(lambda x:database_client.get_nn(x))
    return links_df

def get_links_df_with_locations(database_client):
    links_df = get_clean_link_df(database_client)
    links_df['to_latitude'] = links_df['to'].apply(lambda x: nn_to_latitude(x, database_client))
    links_df['to_longitude'] = links_df['to'].apply(lambda x: nn_to_longitude(x, database_client))
    links_df['from_latitude'] = links_df['from'].apply(lambda x: nn_to_latitude(x, database_client))
    links_df['from_longitude'] = links_df['from'].apply(lambda x: nn_to_longitude(x, database_client))

    return links_df
    

def create_shortest_path_graph(database_client):
    # TODO: look through all supernodes
    # supernode_nns = [1932, 227, 713]
    supernode_nn = 1932

    signup_df = database_client.signup_df.copy()
    active_nodes = signup_df[signup_df['Status'].isin(['Installed', 'NN assigned'])]
    active_nodes = active_nodes[active_nodes['NN'] != 0]
     
    links_df = get_clean_link_df(database_client)
     
    graph = nx.from_pandas_edgelist(links_df, 'to', 'from')

    used_active_nns = []
    shortest_paths = []
    for nn in active_nodes['NN']:
        try:
            path = list(nx.shortest_path(graph, nn, supernode_nn))
            shortest_paths.append(path)
            used_active_nns.append(nn)
        except Exception as e:
            pass
    
    return shortest_paths, used_active_nns

def get_downstream_nns(hub_nn:int, database_client, shortest_paths, active_nns):

    downstream_nns = []
    for nn, path in zip(active_nns, shortest_paths):
        if hub_nn in path and nn != hub_nn:
            downstream_nns.append(nn)

    downstream_nns = list(set(downstream_nns))

    return downstream_nns

if __name__ == "__main__":
 
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

    # shortest_paths, active_nns = create_shortest_path_graph(database_client)

    # nns = get_downstream_nns(2274, database_client, shortest_paths, active_nns)
    # print(nns)

    links_df = get_links_df_with_locations(database_client)
    print(links_df.head())