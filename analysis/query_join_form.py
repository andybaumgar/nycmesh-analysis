import os

from dotenv import load_dotenv

load_dotenv()

import mesh_database_client

spreadsheet_id = os.environ.get("SPREADSHEET_ID")
database_client = mesh_database_client.DatabaseClient(
    spreadsheet_id=spreadsheet_id, include_active=True
)

df = database_client.active_node_df
email_df = df[["Email", "Name", "NN", "Timestamp"]]
print(df)
