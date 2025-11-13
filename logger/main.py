import json
import time
import datetime
import argparse
import logging

from database_value_logger import DatabaseValueLogger
from froeling_modbus import Lambdatronic3200Modbus

logger = logging.getLogger(__name__)


def getSleepTime(interval_minutes: int = 6) -> float:
    now = datetime.datetime.now()
    next_wake_time = now + datetime.timedelta(minutes=interval_minutes)
    next_wake_time = next_wake_time.replace(minute=(next_wake_time.minute // interval_minutes) * interval_minutes, second=0, microsecond=0)
    
    logger.debug(f"Next wake time is {next_wake_time}.")
    
    return (next_wake_time - now).total_seconds()

def main(db_file: str, sensors: dict[str, dict[str, int|str]], logging_interval: int, debug: bool) -> None:
    logging.basicConfig(
        filename="froeling_sensor_logger.log",
        format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
        level=logging.DEBUG if debug else logging.INFO
    )

    database_logger = DatabaseValueLogger(db_file=db_file, sensors=sensors)
    sensor_connection = Lambdatronic3200Modbus(
        port="/dev/ttyUSB0", 
        modbus_addr=1,
        connection_mode="rtu"
    )
    
    if debug:
        sensor_connection.debug_mode(True)
    
    while True:
        time.sleep(getSleepTime(logging_interval))
        sensor_values = sensor_connection.read_sensors(sensors)
        database_logger.log_froeling(sensor_values)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Froeling Sensor Logger")
    argparser.add_argument("--config", type=str, required=True, help="Path to configuration file")
    argparser.add_argument("--interval", type=int, default=6, help="Logging interval in minutes")
    argparser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = argparser.parse_args()

    with open(args.config, "r") as config_file:
        config = json.load(config_file)
        main(config["database_name"], config["sensors"], args.interval, debug=args.debug)
