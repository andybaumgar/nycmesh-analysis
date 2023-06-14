## Grafana setup

docker run -d --name=grafana -p 3000:3000 grafana/grafana:8.5.0

## Influx setup

docker compose up -d --force-recreate --build