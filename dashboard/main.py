import argparse
import json
import os
from typing import Iterable
import streamlit as st
import sqlite3
import numpy as np
import datetime


def get_data_from_db(db_file: str) -> dict[str, np.ndarray]:
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        data = np.asarray(cursor.execute("SELECT * FROM FROELING_SENSOR_VALUES;").fetchall())
        columns = list(map(lambda x: x[0], cursor.description))
        # timestamps = np.array(list(map(lambda x: x[0], data)), dtype=int)
        # sensor_values = np.array(data, dtype=float)
        sensor_values = {
            columns[i]: np.array(list(map(lambda x: x[i], data)), dtype=float) for i in range(len(columns))
        }
        
        return sensor_values

def filter_dataframe(
    dataframe: dict[str, np.ndarray],
    start: int = None, end: int = None) -> dict[str, np.ndarray]:
    mask = np.ones_like(dataframe["unix_time"], dtype=bool)
    if start is not None:
        mask = mask & (dataframe["unix_time"] >= start)
    if end is not None:
        mask = mask & (dataframe["unix_time"] <= end)

    return {
        k: v[mask] for k, v in dataframe.items()
    } 

def plot_dataframe(
    dataframe: dict[str, np.ndarray], 
    start: int = None, end: int = None, 
    sensors: Iterable[str] | None = None) -> None:
    if sensors is None:
        sensors = dataframe.keys() - ["unix_time"]

    # plot_sensors = st.multiselect(
    #     "Select sensors to display:",
    #     sensors,
    #     default=sensors
    # )
    cols = st.columns(2)
    plot_sensors = []
    for idx, sensor in enumerate(sensors):
        with cols[idx % 2]:
            if st.checkbox(sensor, value=True):
                plot_sensors.append(sensor)

    dataframe = filter_dataframe(dataframe, start, end)
    dataframe["unix_time"] = list(map(
        lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"),
        dataframe["unix_time"]))
    
    st.line_chart(dataframe, x="unix_time", y=plot_sensors, x_label="Time", y_label="Sensor Values")

argparser = argparse.ArgumentParser(description='Visualize sensor data from Froeling heater.')
argparser.add_argument("--config", type=str, required=True, help="Path to configuration file")
try:
    args = argparser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)
with open("config.json", 'r') as config_file:
    config = json.load(config_file)

st.title('Froeling Heater Sensor Data')

dataframe = get_data_from_db(config["database_name"])

start_time, end_time = st.select_slider(
    "Select time range to display:",
    options=dataframe["unix_time"],
    value=(dataframe["unix_time"][0], dataframe["unix_time"][-1]),
    format_func=lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))

plots = [
    ("hot_water_storage_temp_bottom", "hot_water_storage_temp_middle", "hot_water_storage_temp_top", "hot_water_storage_loading_level"),
    ("heating_circuit_temp_in", "heating_circuit_temp_out"),
    ("outdoor_temp", "furnace_temp")
]

for sensors in plots:
    plot_dataframe(dataframe, start_time, end_time, sensors)
