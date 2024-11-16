import datetime
import unittest

from zambretti_py.zambretti import PressureData, Trend, Zambretti


class TestPressureTrendCalculation(unittest.TestCase):
    def test_truncating_data_points(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now, 1023.0),
                (now - datetime.timedelta(minutes=20), 1023.0),
                (now - datetime.timedelta(hours=1, minutes=19), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1023.0),
            ]
        )
        zambretti = Zambretti()
        truncated_data_points = zambretti._truncate_time_data_to_three_last_hours(
            pressure_data=pressure_data
        )

        self.assertEqual(pressure_data, truncated_data_points)

    def test_truncating_data_points_truncates_older_than_three_hours(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now, 1023.0),
                (now - datetime.timedelta(minutes=20), 1023.0),
                (now - datetime.timedelta(hours=1, minutes=19), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1023.0),
                (now - datetime.timedelta(hours=3), 1023.0),
                (now - datetime.timedelta(hours=6, minutes=12), 1023.0),
            ]
        )
        zambretti = Zambretti()
        truncated_data_points = zambretti._truncate_time_data_to_three_last_hours(
            pressure_data=pressure_data
        )

        expected = PressureData(
            [
                (now, 1023.0),
                (now - datetime.timedelta(minutes=20), 1023.0),
                (now - datetime.timedelta(hours=1, minutes=19), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1023.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1023.0),
            ]
        )

        self.assertEqual(
            expected,
            truncated_data_points,
        )

    def test_filtering_data_points_by_pressure_value(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(minutes=20), 1000.0),
                (now - datetime.timedelta(hours=1, minutes=19), 1010.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1020.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1030.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1040.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1050.0),
            ]
        )
        zambretti = Zambretti()
        truncated_data_points = zambretti._filter_time_data_by_pressure_values(
            min_value=1001, max_value=1030, pressure_data=pressure_data
        )

        expected = PressureData(
            [
                (now - datetime.timedelta(hours=1, minutes=19), 1010.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1020.0),
                (now - datetime.timedelta(hours=2, minutes=59), 1030.0),
            ]
        )

        self.assertEqual(
            expected,
            truncated_data_points,
        )

    def test_calculating_sea_level_pressure(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(minutes=20), 1000),
            ]
        )
        zambretti = Zambretti()

        sea_level_pressure = zambretti._convert_to_sea_level_pressure(
            elevation=100, temperature=10, pressure_data=pressure_data
        )
        assert sea_level_pressure == PressureData(points=[(now, 1012.13)])

    def test_checking_pressure_difference_falling(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1054),
                (now - datetime.timedelta(hours=2, minutes=49), 1053),
                (now - datetime.timedelta(hours=2, minutes=39), 1052),
                (now - datetime.timedelta(hours=2, minutes=12), 1040),
                (now - datetime.timedelta(hours=1, minutes=19), 1039),
                (now - datetime.timedelta(minutes=20), 1038),
            ]
        )
        zambretti = Zambretti()

        assert zambretti._get_pressure_difference(pressure_data) == -14

    def test_checking_pressure_difference_rising(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1044),
                (now - datetime.timedelta(hours=2, minutes=49), 1045),
                (now - datetime.timedelta(hours=2, minutes=39), 1046),
                (now - datetime.timedelta(hours=2, minutes=12), 1050),
                (now - datetime.timedelta(hours=1, minutes=19), 1051),
                (now - datetime.timedelta(minutes=20), 1052),
            ]
        )
        zambretti = Zambretti()

        assert zambretti._get_pressure_difference(pressure_data) == 6

    def test_calculating_trend_falling(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1006),
                (now - datetime.timedelta(hours=2, minutes=49), 1005),
                (now - datetime.timedelta(hours=2, minutes=39), 1004.90),
                (now - datetime.timedelta(hours=2, minutes=12), 1000.80),
                (now - datetime.timedelta(hours=1, minutes=19), 1000.50),
                (now - datetime.timedelta(minutes=20), 1000),
            ]
        )
        zambretti = Zambretti()

        trend = zambretti.calculate_trend(pressure_data)

        self.assertEqual(trend, Trend.FALLING)

    def test_calculating_trend_steady(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1000),
                (now - datetime.timedelta(hours=2, minutes=49), 1001),
                (now - datetime.timedelta(hours=2, minutes=39), 1001),
                (now - datetime.timedelta(hours=2, minutes=12), 1001),
                (now - datetime.timedelta(hours=1, minutes=19), 1000.90),
                (now - datetime.timedelta(minutes=20), 1000.90),
            ]
        )
        zambretti = Zambretti()

        trend = zambretti.calculate_trend(pressure_data)

        self.assertEqual(trend, Trend.STEADY)

    def test_calculating_trend_rising(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1000),
                (now - datetime.timedelta(hours=2, minutes=49), 1001),
                (now - datetime.timedelta(hours=2, minutes=39), 1001),
                (now - datetime.timedelta(hours=2, minutes=12), 1001),
                (now - datetime.timedelta(hours=1, minutes=19), 1003.90),
                (now - datetime.timedelta(minutes=20), 1004.90),
            ]
        )
        zambretti = Zambretti()

        trend = zambretti.calculate_trend(pressure_data)

        self.assertEqual(trend, Trend.RISING)
