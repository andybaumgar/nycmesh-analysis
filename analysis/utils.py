from pathlib import Path

def get_data_file_path(data_filename):
    data_path_object = Path(__file__).parent.parent / 'data'
    data_file_path =  str(data_path_object / data_filename)
    return data_file_path