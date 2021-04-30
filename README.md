# Enviro+ to InfluxDB

Push metrics from Enviro+ to InfluxDB for Grafana.

Adjust database parameters before first use.

Gas readings were calibrated according to https://forums.pimoroni.com/t/enviro-ohms-to-ppm/12207/6, sensors need 100mins of warm-up before first database push for accurate PPM readings.
This is really important - each RPi and Enviro board can produce different outputs!

### How to reliably run it
It's important that sensors run in a consistent matter - for accurate readings.
`Supervisor` can monitor python PID and make sure it's always up:

`sudo apt-get install supervisor`

`sudo mkdir /var/log/enviro`

`sudo nano /etc/supervisor/conf.d/enviro.conf` :

```
[program:enviro]
command=python measurements_to_influx.py
directory=/home/pi/GitHub/enviro
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/enviro/measurements_to_influx.err.log
stdout_logfile=/var/log/enviro/measurements_to_influx.out.log
user=pi
```

`sudo supervisorctl reread`

`sudo supervisorctl update`
