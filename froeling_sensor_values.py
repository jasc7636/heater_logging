from dataclasses import dataclass

@dataclass
class FroelingSensorValues:
    hot_water_storage_temp_bottom: float
    hot_water_storage_temp_middle: float
    hot_water_storage_temp_top: float
    heating_circuit_temp_in: float
    heating_circuit_temp_out: float
    outdoor_temp: float
