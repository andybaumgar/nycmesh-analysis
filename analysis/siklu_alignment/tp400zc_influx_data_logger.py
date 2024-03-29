import tp4000zc
from time import sleep

from http.server import BaseHTTPRequestHandler, HTTPServer
from influxdb import InfluxDBClient
from datetime import datetime
import json

port = '/dev/cu.usbserial-10'
dmm = tp4000zc.Dmm(port=port)

influx_client = InfluxDBClient('localhost', 8086, 'admin', 'admin', 'siklu')

def get_voltage():
    val = dmm.read()

    print(val.numericVal)
    return val.numericVal


def create_influx_post(measurements):
    json_body = []
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    for key, value in measurements.items():
        json_part = {
            "measurement": key,
            "time": current_time,
            "fields": {
                "value": value
            }
        }

        json_body.append(json_part)

    return json_body

def record_data():  
    try:
        data = {"voltage": abs(get_voltage())}
        
        post = create_influx_post(data)
        influx_client.write_points(post)
    except:
        pass

while(True):
    sleep(.1)
    record_data()

dmm.close()