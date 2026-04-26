# A minimalistic python interface for PMS7003 sensor

This is a rewrite of Thomas Lewicki's [PMS7003 interface](https://github.com/tomasz-lewicki/pms7003).

The code reads particulate matter concentrations from a serial port.
Tested on Raspberry Pi, but it should work on any machine with Python and serial port.

For testing purposes, there is functionality in the `test_utils` folder to generate synthetic readings.

See [here](https://aqicn.org/sensor/pms5003-7003/) for a description of the physical device, or see the PDF in the `docs` folder.

## Setup

Assuming you use `uv` to manage your dependencies, you can add this library to your virtual environment with 

```bash
uv add "pms7003 @ git+https://github.com/boyeah/pms7003.git"
```

### Raspberry configuration and connection

Serial communication must be enabled on the Raspberry.
This can be done either in the Raspberry Pi Configuration desktop app or in `raspi-config`.
Either way, you want to *disable* the Serial Console option, and *enable* the Serial Port option.
In `raspi-config`, these options are prompted as consecutive questions.

See [This guide](https://fleetstack.io/blog/raspberry-pi-serial) for more info.

On the Raspberry Pi 5, the primary UART is exposed through a dedicated debug header, and `/dev/serial0` points to `/dev/ttyAMA10` (vs. `/dev/ttyAMA0` on other versions), i.e. `/dev/serial0` doesn't read from the GPIO pins (see [Raspberry configuration docs](https://www.raspberrypi.com/documentation/computers/configuration.html#serial-port)). 
This means that on the Raspberry Pi 5, you must connect to `/dev/ttyAMA0` directly if you have connected the PMS7003 to the GPIO pins.

## Usage example

See `example.py` or `example_threading.py` for simple usage examples.

