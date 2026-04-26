import time

from pms7003 import Pms7003Sensor

with Pms7003Sensor('/dev/ttyAMA0') as sensor:
    while True:
        print(sensor.read_measurement())
        time.sleep(1)