from analysis.uisp_client import load_uisp_data_from_file, devices_to_df, get_device_history

def test_get_device_history():
    device_id = '673cb9d4-7365-4714-8129-1c38cd697988'
    history = get_device_history(device_id)

if __name__ == '__main__':
    test_get_device_history()