from dotenv import load_dotenv
import os

import mesh_database_client
from mesh_utils import get_downstream_nns

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

def hub_to_emails(hub_nn, paste_format=True):
    linked_nns = database_client.nn_to_linked_nn(hub_nn)
    linked_nns = [database_client.get_nn(x) for x in linked_nns]

    df = database_client.signup_df.copy()

    df = df[df['NN'].isin(linked_nns)]
    emails = df['Email'].tolist()

    if paste_format:
        return " ".join(emails)

    return emails

if __name__ == "__main__":
    nns_basic = database_client.nn_to_linked_nn(2274)
    nns_basic = [database_client.get_nn(x) for x in nns_basic]
    nns_shortest_path = get_downstream_nns(2274, database_client)
    # print(nns_basic)
    # print(nns_shortest_path)

    difference = list(set(nns_shortest_path)-set(nns_basic))
    print(difference)

    # emails_basic = hub_to_emails(2274)
    # print(emails)