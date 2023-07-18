import re
from analysis.utils import nn_to_latitude, nn_to_longitude

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

def get_links_df_with_locations(database_client):
    links_df = database_client.active_link_df
    links_df['to_latitude'] = links_df['to'].apply(lambda x: nn_to_latitude(x, database_client))
    links_df['to_longitude'] = links_df['to'].apply(lambda x: nn_to_longitude(x, database_client))
    links_df['from_latitude'] = links_df['from'].apply(lambda x: nn_to_latitude(x, database_client))
    links_df['from_longitude'] = links_df['from'].apply(lambda x: nn_to_longitude(x, database_client))

    return links_df
    