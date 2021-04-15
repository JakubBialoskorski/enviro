#!/usr/bin/env python3

import time
from time import gmtime
from bme280 import BME280
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from influxdb import InfluxDBClient

# InfluxDB endpoint configuration
host = "" # set IP or DNS name here
port = 8086
dbname = "" # set DB name
user = "" # set database username
password="" # set database password
interval = 5 # adjust as you see fit
client = InfluxDBClient(host, port, user, password, dbname)
# Required parameters
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp
# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up. Default is 2.25 .
factor = 1.75
cpu_temps = [get_cpu_temperature()] * 5

while True:
    # Temperature section
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    # Pressure section
    pressure = bme280.get_pressure()
    # Humidity section
    humidity = bme280.get_humidity()
    # Hack time to properly display in Grafana
    iso = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    json_body = [
        {
            "measurement": "Enviro+",
            "tags": {
                "host": "enviro"
            },
            "time": iso,
            "fields": {
                "temperature": comp_temp,
                "pressure": pressure,
                "humidity": humidity
            }
        }
    ]
    client.write_points(json_body)
    print("write points: {0}".format(json_body)) # for debugging, can be commented - out
    time.sleep(interval)