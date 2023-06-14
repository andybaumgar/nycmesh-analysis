## Note
- Only tested on Mac

## Hardware
This project uses a [TP4000zc multimeter](https://www.amazon.com/gp/product/B000OPDFLM/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1).

## Setup

- cd into `analysis/siklu_alignment`
- start Docker Desktop
- `docker compose up -d --force-recreate --build`
- in Grafana to setup the InfluxDB datasource use host url: `http://influxdb:8086`, database: `siklu`, password/username: `admin`
- `pip install influxdb`
- run `tp400zc_influx_data_logger.py`
- in Grafana create a dashboard and a panel with the voltage metric

## Troubbleshooting 
- if the serial port is incorrect you may have to run `read_serial_ports_mac.py` to determine the correct port for your system