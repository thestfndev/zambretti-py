import datetime
import math
from dataclasses import dataclass
from enum import Enum

from statistics import mean


class Trend(Enum):
    FALLING = 1
    STEADY = 2
    RISING = 3
    UNKNOWN = 4


class WindDirection(Enum):
    NORTH = 0
    SOUTH = 2
    WEST = 1
    EAST = 1


@dataclass
class PressureData:
    points: list[tuple[datetime.datetime, float]]

    def sorted_by_time(self):
        return PressureData(points=sorted(self.points, key=lambda x: x[0]))


class Zambretti:
    PRESSURE_LOOKUP_TABLE = {
        Trend.FALLING: {
            1: "Settled Fine",
            2: "Fine Weather",
            3: "Fine, Becoming Less Settled",
            4: "Fairly Fine, Showery Later",
            5: "Showery, Becoming More Unsettled",
            6: "Unsettled, Rain Later",
            7: "Rain at Times, Worse Later",
            8: "Rain at Times, Becoming Very Unsettled",
            9: "Very Unsettled, Rain",
        },
        Trend.STEADY: {
            10: "Settled Fine",
            11: "Fine Weather",
            12: "Fine, Possibly Showers",
            13: "Fairly Fine, Showers Likely",
            14: "Showery, Bright Intervals",
            15: "Changeable, Some Rain",
            16: "Unsettled, Rain at Times",
            17: "Rain at Frequent Intervals",
            18: "Very Unsettled, Rain",
            19: "Stormy, Much Rain",
        },
        Trend.RISING: {
            20: "Settled Fine",
            21: "Fine Weather",
            22: "Becoming Fine",
            23: "Fairly Fine, Improving",
            24: "Fairly Fine, Possibly Showers Early",
            25: "Showery Early, Improving",
            26: "Changeable, Mending",
            27: "Rather Unsettled, Clearing Later",
            28: "Unsettled, Probably Improving",
            29: "Unsettled, Short Fine Intervals",
            30: "Very Unsettled, Finer at Times",
            31: "Stormy, Possibly Improving",
            32: "Stormy, Much Rain",
        },
    }

    def _truncate_time_data_to_three_last_hours(
        self, pressure_data: PressureData
    ) -> PressureData:
        now = datetime.datetime.now()
        three_hours_ago = now - datetime.timedelta(hours=3)

        truncated_list = []

        for point in pressure_data.points:
            if three_hours_ago <= point[0]:
                truncated_list.append(point)
        return PressureData(points=truncated_list)

    def _filter_time_data_by_pressure_values(
        self, min_value: float, max_value: float, pressure_data: PressureData
    ) -> PressureData:
        filtered_list = []

        for point in pressure_data.points:
            if min_value <= point[1] <= max_value:
                filtered_list.append(point)
        return PressureData(points=filtered_list)

    def _get_pressure_difference(self, pressure_data: PressureData) -> float:
        """Get the pressure difference between the start and end of
         measurements.

        To better handle momentary pressure spikes, the average of the first and
        last three measurements is used.
        """
        initial_pressure = mean(
            [
                pressure_data.points[0][1],
                pressure_data.points[1][1],
                pressure_data.points[2][1],
            ]
        )
        final_pressure = mean(
            [
                pressure_data.points[-1][1],
                pressure_data.points[-2][1],
                pressure_data.points[-3][1],
            ]
        )
        return round(final_pressure - initial_pressure, 2)

    def calculate_trend(self, pressure_data: PressureData) -> Trend:
        pressure_data = self._truncate_time_data_to_three_last_hours(pressure_data)
        pressure_data = pressure_data.sorted_by_time()
        filtered_for_falling = self._filter_time_data_by_pressure_values(
            min_value=985, max_value=1050, pressure_data=pressure_data
        )
        filtered_for_steady = self._filter_time_data_by_pressure_values(
            min_value=960, max_value=1033, pressure_data=pressure_data
        )
        filtered_for_rising = self._filter_time_data_by_pressure_values(
            min_value=947, max_value=1030, pressure_data=pressure_data
        )
        if self._get_pressure_difference(filtered_for_falling) < -1.6:
            return Trend.FALLING
        if self._get_pressure_difference(filtered_for_rising) > 1.6:
            return Trend.RISING
        if (
            self._get_pressure_difference(filtered_for_steady) > -1.6
            and self._get_pressure_difference(filtered_for_steady) < 1.6
        ):
            return Trend.STEADY
        return Trend.UNKNOWN

    def forecast(
        self,
        pressure: float,
        elevation: int,
        temperature: float,
        pressure_data: PressureData,
        wind_direction: WindDirection | None = None,
    ) -> str:
        forecast = 0
        sea_level_pressure = pressure * pow(
            1 - (0.0065 * elevation) / (temperature + (0.0065 * elevation) + 273.15),
            -5.257,
        )
        trend = self.calculate_trend(pressure_data)
        if trend == trend.UNKNOWN:
            return "Could not determine the pressure trend from available data"
        if trend == Trend.FALLING:
            forecast = math.floor(127 - 0.12 * sea_level_pressure)
        if trend == Trend.STEADY:
            forecast = math.floor(144 - 0.13 * sea_level_pressure)
        if trend == Trend.RISING:
            forecast = math.floor(185 - 0.16 * sea_level_pressure)

        if wind_direction:
            forecast += wind_direction.value

        return self.PRESSURE_LOOKUP_TABLE[trend].get(
            forecast, "Could not forecast the weather from available data"
        )
