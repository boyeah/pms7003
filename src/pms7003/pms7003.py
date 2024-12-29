"""A minimalistic python interface for PMS7003 sensor"""

from dataclasses import dataclass
from datetime import datetime
from typing import Self

import serial


class PmsSensorException(Exception):
    """
    Implies a problem with sensor communication that is unlikely to re-occur
    (e.g. serial connection glitch). Prevents from returning corrupt
    measurements.
    """

    pass


@dataclass
class Measurement:
    timestamp: datetime

    pm1_0_cf1: int
    pm2_5_cf1: int
    pm10_cf1: int

    pm1_0_atm: int
    pm2_5_atm: int
    pm10_atm: int

    n0_3: int
    n0_5: int
    n1_0: int
    n2_5: int
    n5_0: int
    n10: int

    @classmethod
    def from_values(cls, timestamp: datetime, values: list[int]) -> Self:
        return cls(timestamp, *values)


class Pms7003Sensor:
    START_SEQUENCE = bytes([0x42, 0x4D])
    FRAME_BYTES = 30

    SERIAL_CONFIG = {
        "baudrate": 9600,
        "bytesize": serial.EIGHTBITS,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
    }

    def __init__(self, port, timeout=2):
        # Values according to product data manual
        self._serial = serial.Serial(
            port=port,
            timeout=timeout,
            **self.SERIAL_CONFIG,
        )

    def close(self):
        self._serial.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _read_frame(self) -> bytes:
        """
        :return: Read a frame and return the bytes read
        """
        self._serial.read_until(self.START_SEQUENCE)
        frame = self._serial.read(self.FRAME_BYTES)
        if len(frame) != self.FRAME_BYTES:
            raise PmsSensorException("Failed to read data from serial port")
        return frame

    def _frame_to_ints(self, frame: bytes, n: int) -> list[int]:
        """
        :return: a list of n integer values converted from two-byte values in
            the frame
        """
        return [int.from_bytes(frame[i * 2 : i * 2 + 2], "big") for i in range(n)]

    def _read_measured_values(self) -> list[int]:
        """
        :return: a frame as a list of integer values of bytes
        """
        frame = self._read_frame()

        # According to the documentation here are two reserved bytes after the
        # data and before the checksum, these contain random values, so we just
        # ignore them.
        frame_length = self._frame_to_ints(frame, 1)[0]
        data = self._frame_to_ints(frame[2:], 12)
        checksum = self._frame_to_ints(frame[-2:], 1)[0]

        if frame_length != self.FRAME_BYTES - 2:
            raise PmsSensorException(
                "Unexpected frame length read from serial. "
                f"Expected {self.FRAME_BYTES - 2}, got {frame_length}."
            )

        self._validate_frame(frame, checksum)
        return data

    def _validate_frame(self, frame, checksum):
        if checksum != sum(frame[:-2]) + sum(self.START_SEQUENCE):
            raise PmsSensorException("Checksum error")

    def wakeup(self):
        with self._serial as s:
            command = bytearray([0x42, 0x4D, 0xE4, 0x00, 0x01, 0x01, 0x74])
            s.write(command)

    def sleep(self):
        with self._serial as s:
            command = bytearray([0x42, 0x4D, 0xE4, 0x00, 0x00, 0x01, 0x73])
            s.write(command)

    def read_measurement(self) -> Measurement:
        """
        :return: a Measurement with measurements. Raises Pms7003Exception in case
            of a problem.
        """
        values = self._read_measured_values()
        return Measurement.from_values(datetime.now().astimezone(), values)
