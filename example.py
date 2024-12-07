from pms7003 import Pms7003Sensor, PmsSensorException

max_failures = 3

if __name__ == "__main__":
    with Pms7003Sensor("/dev/ttyAMA0") as sensor:
        failures = 0
        while failures < max_failures:
            try:
                data = sensor.read_measurement()
                print(data)
            except PmsSensorException as e:
                print(f"Connection problem: {e}")
                failures += 1
            if failures == max_failures:
                print("Too many failures, giving up.")
                break
