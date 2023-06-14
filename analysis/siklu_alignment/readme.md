## Setup

- cd into `analysis/siklu_alignment`
- start Docker Desktop
- `docker compose up -d --force-recreate --build`
- in Grafana to setup the InfluxDB datasource use host url: `http://influxdb:8086`, database: `siklu`, password/username: `admin`
- `pip install influxdb`
- run `tp400zc_influx_data_logger.py`
- in Grafana create a dashboard and a panel with the voltage metric