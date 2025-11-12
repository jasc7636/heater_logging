import minimalmodbus
import serial

class Lambdatronic3200Modbus:
    def __init__(self, port: str, modbus_addr: int, connection_mode: str, sensors: dict[str, dict[str, int|str]]) -> None:
        if connection_mode.lower() == "rtu":
            connection_mode = minimalmodbus.MODE_RTU
        elif connection_mode.lower() == "ascii":
            connection_mode = minimalmodbus.MODE_ASCII
        else:
            raise ValueError("Invalid connection mode. Use 'rtu' or 'ascii'.")
        
        self.instrument = minimalmodbus.Instrument(port, modbus_addr, connection_mode)
        self.instrument.BAUDRATE = 57600
        self.instrument.PARITY = serial.PARITY_NONE
        self.instrument.STOPBITS = serial.STOPBITS_ONE
        self.instrument.BYTESIZE = serial.EIGHTBITS
        self.instrument.TIMEOUT = 1
        self.instrument.debug = self.debug
        
        self.sensors = sensors

    def debug_mode(self) -> None:
        self.instrument.debug = True

    def read_sensors(self) -> dict[str, float]:
        pass
