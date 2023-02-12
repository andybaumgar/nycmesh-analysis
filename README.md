# nyc-mesh-analysis 

Scripts to analyize NYC Mesh network data

## Setup
- Clone this repository to your computer.
- Ensure you have [Python](https://www.python.org/downloads/) with pip installed.
- Open a terminal in the root repository directory.
- `pip install -r requirements.txt`
- `pip install -e .`
- Copy the the `.env-example` file and rename it to `.env`.  Fill in any relevant credentials, or copy paste from an existing .env.
- Download appropriate release of [nycmesh-tool CLI](https://github.com/byxorna/nycmesh-tool/releases) for your system.
- Rename the executable and add it to the system path so it is callable by `nycmesh-tool`.  You may need to restart your IDE / terminal.

## Export UISP LBE Strength
- Run the file `analysis/uisp_lbe_strength.py`.
- Files will be exported to the 'data' directory.
- If you want to run the script multiple times to experiment, use the `load_uisp_data_from_file()` function which is currently commented out instead of `get_uisp_devices()`.  This will reduce script run time and UISP calls.