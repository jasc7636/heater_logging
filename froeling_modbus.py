import minimalmodbus
import serial
import logging

logger = logging.getLogger(__name__)

class Lambdatronic3200Modbus:
    """ Connect to a Fröling Lambdatronic 3200 via Modbus to read current values. For details on the communication protocol see https://www.holzheizer-forum.de/attachment/37208-b1200522-modbus-lambdatronic-3200-50-04-05-19-de-1-pdf/
    """
    
    def __init__(self, port: str, modbus_addr: int, connection_mode: str) -> None:
        if connection_mode.lower() == "rtu":
            connection_mode = minimalmodbus.MODE_RTU
        elif connection_mode.lower() == "ascii":
            connection_mode = minimalmodbus.MODE_ASCII
        else:
            logger.error("Invalid connection mode. Use 'rtu' or 'ascii'.")
            raise ValueError("Invalid connection mode. Use 'rtu' or 'ascii'.")

        self.instrument = minimalmodbus.Instrument(port, modbus_addr, connection_mode)
        self.instrument.BAUDRATE = 57600
        self.instrument.PARITY = serial.PARITY_NONE
        self.instrument.STOPBITS = serial.STOPBITS_ONE
        self.instrument.BYTESIZE = serial.EIGHTBITS
        self.instrument.TIMEOUT = 1

    def debug_mode(self, debug=True) -> None:
        self.instrument.debug = debug
        logger.debug(f"Modbus debug mode {'enabled' if debug else 'disabled'}.")

    def read_sensors(self, sensors: dict[str, dict[str, int|str]]) -> dict[str, float]:
        logger.debug("Reading sensor values.")

        sensor_values: dict[str, float] = {}
        for sensor_name, sensor in sensors.items():
            try:
                sensor_values[sensor_name] = self.instrument.read_register(
                    registeraddress=sensor["modbus_offset"],
                    number_of_decimals=sensor["decimal_places"],
                    functioncode=4,
                    signed=True
                )
            except KeyError:
                logger.error(f"Sensor '{sensor_name}' config is incomplete.")
            except IOError:
                logger.error(f"Failed to read sensor '{sensor_name}'.")

        return sensor_values
