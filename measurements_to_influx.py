#!/usr/bin/env python3

import time
from math import log10
from enviroplus import gas
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
password= "" # set database password
interval = 10 # adjust as you see fit
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
factor = 1.25
cpu_temps = [get_cpu_temperature()] * 5

while True:
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    gas_data = gas.read_all()
    oxidising = gas_data.oxidising
    reducing = gas_data.reducing
    nh3 = gas_data.nh3

    # oxidising, NO2: ppm = Rs /(6.5 * R0)
    NO2_PPM = gas_data.oxidising/6.5/1230000 # R0 chosen to give value approx 0.01 in fresh air (detectable = 0.05 to 10)
    # reducing,CO: ppm = 10^((log10(Rs / 3.5 / R0)) / -0.845 )
    CO_PPM = 10**((log10(gas_data.reducing/3.5/162000)) / -0.845) # R0 chosen to give value approx 2 in fresh air (detectable = 1 to 1000)
    # NH3: ppm = =10^((log10(Rs / 0.77 / R0)) / -0.5335 )
    NH3_PPM = 10**((log10(gas_data.nh3/0.77/298000)) / -0.5335) # R0 chosen to give value approx 2 in fresh air (detectable = 1 to 300)

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
                "humidity": humidity,
                "oxidising": gas_data.oxidising,
                "reducing": gas_data.reducing,
                "nh3": gas_data.nh3,
                "oxidising_ppm": NO2_PPM,
                "reducing_ppm": CO_PPM,
                "nh3_ppm": NH3_PPM
            }
        }
    ]
    client.write_points(json_body)
    # print("write points: {0}".format(json_body))
    time.sleep(interval)
