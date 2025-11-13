import sqlite3
import logging

logger = logging.getLogger(__name__)

class DatabaseValueLogger:
    def __init__(self, db_file: str, sensors: dict[str, dict[str, int|str]]) -> None:
        self.sensors = sensors

        logger.debug(f"Connecting to database {db_file}.")
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_table()
        
        self._sql_insert = """
            INSERT INTO FROELING_SENSOR_VALUES (
                {}
            ) VALUES (
                {}
            );
            """.format(",".join(self.sensors.keys()), ",".join("?" for _ in self.sensors))
    
    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS FROELING_SENSOR_VALUES (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                {}
            );""".format(",".join(self.sensors.keys()))
        )
        
        # Verify columns in case the table already existed
        self.cursor.execute("PRAGMA table_info('FROELING_SENSOR_VALUES');")
        column_names = (row[1] for row in self.cursor.fetchall())
        if not all(column in column_names for column in self.sensors.keys()):
            logger.error("Database columns do not match sensor config.")
            raise ValueError("Database columns do not match sensor config.")
    
    def log_froeling(self, sensor_values: dict[str, float]) -> None:
        logger.debug("Writing sensor values to database.")

        sensor_value_tuple = (sensor_values[sensor] for sensor in self.sensors)
        self.cursor.execute(self._sql_insert, sensor_value_tuple)
        self.connection.commit()
        
    def close(self) -> None:
        logger.debug("Closing database connection.")
        self.connection.close()
