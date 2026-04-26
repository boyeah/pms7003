from threading import Lock, Thread
from types import TracebackType
from typing import Any, Self

from .pms7003 import Measurement, Pms7003Sensor, PmsSensorException
from .utils import logger


class Pms7003Thread(Thread):
    def __init__(self, max_failures: int = -1, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._lock = Lock()
        self._sensor = self._create_sensor(*args, **kwargs)
        self._measurements: list[Measurement] = []
        self._running = False
        self._max_failures = max_failures

    def _create_sensor(self, *args: Any, **kwargs: Any) -> Pms7003Sensor:
        return Pms7003Sensor(*args, **kwargs)

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.stop()

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False
        self.join()
        self._sensor.close()
        logger.info("PMS7003 sensor thread stopped successfully")

    def run(self) -> None:
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

    def get_measurements(self) -> list[Measurement]:
        with self._lock:
            val = self._measurements
            self._measurements = []
        return val
