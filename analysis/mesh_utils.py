import re
import mesh_database_client
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

def get_downstream_nns(hub_nn:int, database_client):
    
    # TODO: look through all supernodes
    supernode_nns = [1932, 227, 713]

    signup_df = database_client.signup_df.copy()
    active_nodes = signup_df[signup_df['Status'].isin(['Installed', 'NN assigned'])]
    active_nodes = active_nodes[active_nodes['NN'] != 0]
    
    links_df = database_client.links_df.copy()
    links_df = links_df[links_df['status'] != 'dead']

    # convert IN to NN
    for field in ['to', 'from']:        
        links_df[field] = links_df[field].apply(lambda x:database_client.get_nn(x))
    
    graph = nx.from_pandas_edgelist(links_df, 'to', 'from')

    downstream_nns = []
    for nn in active_nodes['NN']:
        try:
            path = list(nx.shortest_path(graph, nn, 227))
            if hub_nn in path:
                downstream_nns.append(nn) 
        except Exception as e:
            pass

    return downstream_nns

if __name__ == "__main__":
 
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

    nns = get_downstream_nns(2274, database_client)
    print(nns)