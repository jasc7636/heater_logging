import sqlite3
from froeling_sensor_values import FroelingSensorValues

class DatabaseValueLogger:
    def __init__(self, db_file="froeling_logs.sqlite3"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_table()
    
    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS FROELING_SENSORS (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                hot_water_storage_temp_bottom REAL,
                hot_water_storage_temp_middle REAL,
                hot_water_storage_temp_top REAL,
                heating_circuit_temp_in REAL,
                heating_circuit_temp_out REAL,
                outdoor_temp REAL
            );
        """)
    
    def log_froeling(self, sensor_values: FroelingSensorValues) -> None:
        self.cursor.execute("""
            INSERT INTO FROELING_SENSORS (
                hot_water_storage_temp_bottom,
                hot_water_storage_temp_middle,
                hot_water_storage_temp_top,
                heating_circuit_temp_in,
                heating_circuit_temp_out,
                outdoor_temp
            ) VALUES (?, ?, ?, ?, ?, ?);
        """, (
            sensor_values.hot_water_storage_temp_bottom,
            sensor_values.hot_water_storage_temp_middle,
            sensor_values.hot_water_storage_temp_top,
            sensor_values.heating_circuit_temp_in,
            sensor_values.heating_circuit_temp_out,
            sensor_values.outdoor_temp
        ))
        self.connection.commit()
        
    def close(self) -> None:
        self.connection.close()
