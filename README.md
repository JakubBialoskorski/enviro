# Enviro+ to InfluxDB

Push metrics from Enviro+ to InfluxDB for Grafana.

Adjust database parameters before first use.

Gas readings were calibrated according to https://forums.pimoroni.com/t/enviro-ohms-to-ppm/12207/6, sensors need 100mins of warm-up before first database push for accurate PPM readings.
This is really important - each RPi and Enviro board can produce different outputs!