from threading import Lock, Thread

from .pms7003 import Pms7003Sensor


class Pms7003Thread(Thread):
    def __init__(self, port):
        super(Pms7003Thread, self).__init__()
        self._lock = Lock()
        self._sensor = Pms7003Sensor(port)
        self._measurements = []
        self._running = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._running = False
        with self._lock:
            self._sensor.close()

    def run(self):
        while self._running:
            with self._lock:
                self._measurements.append(self._sensor.read_measurement())

    def get_measurements(self):
        with self._lock:
            val = self._measurements
            self._measurements = []
        return val
