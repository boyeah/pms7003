import random
from datetime import datetime, timedelta
from typing import Generator

from pms7003 import Measurement

NUM_SENSOR_READINGS = 12


def random_values_generator(
    max_generations: int | None = None,
) -> Generator[list[int], None, None]:
    num_generations = 1
    values = [random.randint(0, 500) for _ in range(NUM_SENSOR_READINGS)]
    yield values
    while num_generations != max_generations:
        values = [max(0, v + int(random.normalvariate(0, 10))) for v in values]
        yield values
        num_generations += 1


def generate_random_measurements(
    minutes: int = 6, frequency: int = 11
) -> list[Measurement]:
    measurements = []
    start_time = datetime.now() - timedelta(minutes=minutes)
    rvs = random_values_generator()
    for i in range(minutes * 60 // frequency):
        timestamp = start_time + timedelta(seconds=i * frequency)
        values = next(rvs)
        measurement = Measurement.from_values(timestamp, values)
        measurements.append(measurement)
    return measurements
