from threading import Lock, Thread

from loguru import logger

from .pms7003 import Pms7003Sensor


class Pms7003Thread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._lock = Lock()
        self._sensor = Pms7003Sensor(*args, **kwargs)
        self._measurements = []
        self._running = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def stop(self):
        with self._lock:
            self._running = False
        self.join()
        self._sensor.close()
        logger.info("PMS7003 sensor thread stopped successfully")

    def run(self):
        logger.info("PMS7003 sensor thread started")
        with self._lock:
            running = self._running
        while running:
            with self._lock:
                measurement = self._sensor.read_measurement()
                self._measurements.append(measurement)
                running = self._running

    def get_measurements(self):
        with self._lock:
            val = self._measurements
            self._measurements = []
        return val
