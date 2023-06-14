## Influx / Grafana setup

- cd into `analysis/siklu_alignment`
- start Docker Desktop
- `docker compose up -d --force-recreate --build`
- in Grafana to setup datasource use host url: `http://influxdb:8086`