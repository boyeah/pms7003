from threading import Lock, Thread

from .pms7003 import Pms7003Sensor, PmsSensorException
from .utils import logger


class Pms7003Thread(Thread):
    def __init__(self, max_failures: int = -1, *args, **kwargs):
        super().__init__()
        self._lock = Lock()
        self._sensor = self._create_sensor(*args, **kwargs)
        self._measurements = []
        self._running = False
        self._max_failures = max_failures

    def _create_sensor(self, *args, **kwargs):
        return Pms7003Sensor(*args, **kwargs)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def stop(self):
        with self._lock:
            if not self._running:
                return
            self._running = False
        self.join()
        self._sensor.close()
        logger.info("PMS7003 sensor thread stopped successfully")

    def run(self):
        logger.info("PMS7003 sensor thread started")
        with self._lock:
            running = self._running = True
        _num_failures = 0
        while running:
            with self._lock:
                try:
                    measurement = self._sensor.read_measurement()
                    self._measurements.append(measurement)
                except PmsSensorException as e:
                    _num_failures += 1
                    if _num_failures == self._max_failures:
                        raise PmsSensorException(
                            f"Max failures reached ({self._max_failures})"
                        ) from e
                    logger.warning("Failed to read measurement: %s", e)
                running = self._running

    def get_measurements(self):
        with self._lock:
            val = self._measurements
            self._measurements = []
        return val
