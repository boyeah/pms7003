import argparse
import itertools
import random
import sys
import time

import serial

from pms7003 import Pms7003Sensor, PmsSensorException


def read(port: str, timeout: int = 2, max_failures: int = 3):
    with Pms7003Sensor(port=port, timeout=timeout) as sensor:
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
                return


def write(port: str, frequency: float = 1.0):
    with serial.Serial(port=port, timeout=100, **Pms7003Sensor.SERIAL_CONFIG) as ser:
        print(f"Opened serial port: {port} for writing frames of fake sensor data")
        sys.stdout.flush()
        frames_written = 0
        while True:
            frame = (
                Pms7003Sensor.START_SEQUENCE
                + int.to_bytes(Pms7003Sensor.FRAME_BYTES - 2, 2, "big")
                + b"".join(
                    itertools.chain(
                        [random.randint(0, 1000).to_bytes(2, "big") for _ in range(12)]
                    )
                )
            )
            reserved = bytes([0, 0])
            checksum = sum(frame).to_bytes(2, "big")
            ser.write(frame + reserved + checksum)
            frames_written += 1
            print(f"Wrote frame number {frames_written}.")
            sys.stdout.flush()
            time.sleep(frequency)


def main():
    parser = argparse.ArgumentParser(
        description="Serial port read/write utility. Run after creating a loopback with socat (socat -d -d pty,raw,echo=0 pty,raw,echo=0)."
    )
    parser.add_argument(
        "mode",
        choices=["read", "write"],
        default="write",
        nargs="?",
        help="Mode of operation: read or write",
    )
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="Serial port to use (get it from socat)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=100,
        help="Timeout for serial port operations",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=1.0,
        help="Frequency of writing frames in write mode",
    )
    args = parser.parse_args()

    if args.mode == "read":
        read(port=args.port, timeout=args.timeout)
    else:
        write(port=args.port, frequency=args.frequency)


if __name__ == "__main__":
    main()
