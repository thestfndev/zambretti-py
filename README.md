# Zambretti Weather Forecasting in Python

This is a Python implementation of the [Zambretti Weather
Forecaster](https://en.wikipedia.org/wiki/Zambretti_Forecaster)

The code is heavily based on the [Zambretti Algorithm for Weather Forecasting
ESP
example](https://github.com/sassoftware/iot-zambretti-weather-forcasting?tab=readme-ov-file)

Further reading: [Short-Range Local Forecasting with a Digital Barograph using
an Algorithm based on the Zambretti
Forecaster.](https://integritext.net/DrKFS/zambretti.htm)

## Usage notes

Pressure data must be provided in millibars or hPa (those are equivalent).
Elevation must be provided in meters.
Temperature must be provided in degrees Celsius.

Minimum 6 readings of atmospheric pressure are required. Best results are when
the pressure readings span the last three hours, but the code will run on any timespan.

## Technical notes

This project has no dependencies, uses only functions from the Python Standard
Library. It should run both in Python and MicroPython.

## Example

Example usage with mock values:

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
    pressure=1013.0,
    elevation=90,
    temperature=25,
    pressure_data=pressure_data,
    wind_direction=WindDirection.NORTH,
)
print(forecast)
```

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