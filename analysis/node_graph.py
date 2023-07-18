import mesh_database_client
from analysis.utils import nn_to_latitude, nn_to_longitude
import networkx as nx
import os

def create_shortest_path_graph(database_client):
    # TODO: look through all supernodes
    # supernode_nns = [1933, 227, 713]
    supernode_nn = 1933

    active_nodes = database_client.active_node_df
     
    links_df = database_client.active_link_df
     
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
        if hub_nn in path and hub_nn != nn:
            downstream_nns.append(nn)

    downstream_nns = list(set(downstream_nns))

    return downstream_nns


if __name__ == "__main__":
 
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id, include_active = True)

    shortest_paths, active_nns = create_shortest_path_graph(database_client)

    # nns = get_downstream_nns(2274, database_client, shortest_paths, active_nns)
    nns = get_downstream_nns(154, database_client, shortest_paths, active_nns)
    print(nns)

    # links_df = get_links_df_with_locations(database_client)
    # print(links_df.head())