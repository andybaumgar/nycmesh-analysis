from dotenv import load_dotenv
import os

import mesh_database_client

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(spreadsheet_id=spreadsheet_id)

def hub_to_emails(hub_nn, paste_format=True):
    linked_nns = database_client.nn_to_linked_nn(hub_nn)

    df = database_client.signup_df.copy()

    df = df[df['NN'].isin(linked_nns)]
    emails = df['Email'].tolist()

    if paste_format:
        emails = " ".join(emails)

    return emails

if __name__ == "__main__":
    emails = hub_to_emails(2274)
    print(emails)