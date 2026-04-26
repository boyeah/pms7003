import random
import time

from pms7003 import Pms7003Thread

if __name__ == "__main__":
    with Pms7003Thread(port="/dev/ttyAMA0", max_failures=3) as sensor:
        while True:
            measurements = sensor.get_measurements()

            print(f"Received {len(measurements)} measurements since last time:")
            print(measurements)
            # We're free to do computation in main thread
            time.sleep(random.randint(1, 4))
