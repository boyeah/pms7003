import time
from unittest.mock import patch

from pms7003.pms7003 import Pms7003Sensor
from pms7003.pms7003_threading import Pms7003Thread
from pms7003.test_utils.generator import random_values_generator


class Pms7003MockSensor(Pms7003Sensor):
    def __init__(self, port, timeout=5, frequency: float = 1.0):
        with patch("serial.Serial"):
            super().__init__(port, timeout)
        self._rvs = random_values_generator()
        self._frequency = frequency

    def _read_measured_values(self) -> list[int]:
        time.sleep(self._frequency)
        return next(self._rvs)


class Pms7003MockThread(Pms7003Thread):
    def _create_sensor(self, *args, **kwargs):
        return Pms7003MockSensor(*args, **kwargs)
