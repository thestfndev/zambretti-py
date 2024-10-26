# Zambretti Weather Forecasting in Python

This is a Python implementation of the [Zambretti Weather
Forecaster](https://en.wikipedia.org/wiki/Zambretti_Forecaster)

The code is heavily based on the [Zambretti Algorithm for Weather Forecasting
ESP
example](https://github.com/sassoftware/iot-zambretti-weather-forcasting?tab=readme-ov-file)

Further reading: [Short-Range Local Forecasting with a Digital Barograph using an Algorithm based on the Zambretti Forecaster.](https://integritext.net/DrKFS/zambretti.htm)

## Usage

Example usage with mock values:

```
import datetime

from zambretti_py.zambretti import PressureData, WindDirection, Zambretti

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
- the current pressure in millibars or hPa (those are equivalent)
- elevation above sea level
- current temperature
- pressure data from the last three hours, or less.
    - data points older than three hours will be removed
    - the pressure data is expected to be provided as a list of tuples, each
      tuple consisting of a datetime.datetime object, and the pressure as float
- optional wind direction, denoting the direction from which the wind is
  flowing. This has a minor effect on the forecast and can be omitted.

The result will be a text description of the forecasted weather. 