# Zambretti Weather Forecasting in Python

This is a Python implementation of the [Zambretti Weather
Forecaster](https://en.wikipedia.org/wiki/Zambretti_Forecaster)

The code is heavily based on the [Zambretti Algorithm for Weather Forecasting
ESP
example](https://github.com/sassoftware/iot-zambretti-weather-forcasting?tab=readme-ov-file)

Further reading: [Short-Range Local Forecasting with a Digital Barograph using
an Algorithm based on the Zambretti
Forecaster.](https://integritext.net/DrKFS/zambretti.htm)

## Python Package

This repository is available as a package in PyPi: [https://pypi.org/project/zambretti-py/](https://pypi.org/project/zambretti-py/)

## Usage notes

To calculate for forecast, the Zambretti algorithm requires:
- elevation above sea level
- current temperature
- pressure data from the last three hours, or less.
    - data points older than three hours will be removed
    - the pressure data is expected to be provided as a list of tuples, each
      tuple consisting of a datetime.datetime object, and the pressure as float
- optional wind direction, denoting the direction from which the wind is
  flowing. This has a minor effect on the forecast and can be omitted.

The result will be a text description of the forecasted weather. 

Pressure data must be provided in millibars or hPa (those are equivalent).
Elevation must be provided in meters.
Temperature must be provided in degrees Celsius.

Minimum 6 readings of atmospheric pressure are required. Best results are when
the pressure readings span the last three hours, but the code will run on any timespan.

## Technical notes

This project has no dependencies, uses only functions from the Python Standard
Library. It should run both in Python and MicroPython.

## Examples

### Example usage with provided pressure data:

```
import datetime

from zambretti_py import PressureData, WindDirection, Zambretti

now = datetime.datetime.now()
pressure_data = PressureData(
    [
        (now - datetime.timedelta(hours=2, minutes=59), 1050.0),
        (now - datetime.timedelta(hours=2, minutes=49), 1040.0),
        (now - datetime.timedelta(hours=2, minutes=39), 1030.0),
        (now - datetime.timedelta(hours=2, minutes=12), 1020.0),
        (now - datetime.timedelta(hours=1, minutes=19), 1010.0),
        (now - datetime.timedelta(minutes=20), 1000.0),
    ]
)
zambretti = Zambretti()

forecast = zambretti.forecast(
    elevation=90,
    temperature=25,
    pressure_data=pressure_data,
    wind_direction=WindDirection.NORTH,
)
print(forecast)
```

### Example usage with loading pressure data from a CSV file:

If you have the pressure history in a CSV file such as this one:

| state  | last_changed                 |
|----------------|---------------------------|
|  988.6          | 2024-11-19T11:33:32.706Z  |
| 988.5          | 2024-11-19T11:34:06.863Z  |
| 988.4          | 2024-11-19T11:37:06.887Z  |

That file can be loaded into `PressureData` by using a `PressureData.from_csv_file`:


```
from zambretti_py import PressureData, WindDirection, Zambretti

pressure_data = PressureData.from_csv_file(
    fname="history.csv",
    timestamp_column_position=1,
    pressure_column_position=0,
    skip_header_rows=1,
    strptime_template="%Y-%m-%dT%H:%M:%S.%fZ",
)

zambretti = Zambretti()

forecast = zambretti.forecast(
    elevation=75,
    temperature=3,
    pressure_data=pressure_data,
    wind_direction=WindDirection.SOUTH,
)
print(forecast)
```

### Example usage with a CSV file generated in Home Assistant:

When you have a sensor in Home Assistant, you can export its history from the
web interface, the result will be a CSV file with this schema:

| entity_id       | state  | last_changed                 |
|--------------|----------------|---------------------------|
| sensor.pressure | 988.6          | 2024-11-19T11:33:32.706Z  |
| sensor.pressure | 988.5          | 2024-11-19T11:34:06.863Z  |
| sensor.pressure | 988.4          | 2024-11-19T11:37:06.887Z  |

That file can be loaded into `PressureData` by using `PressureData.from_home_assistant_csv`:

```
from zambretti_py import PressureData, WindDirection, Zambretti

pressure_data = PressureData.from_home_assistant_csv("history.csv")

zambretti = Zambretti()

forecast = zambretti.forecast(
    elevation=75,
    temperature=3,
    pressure_data=pressure_data,
    wind_direction=WindDirection.SOUTH,
)
print(forecast)
```
