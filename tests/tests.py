import datetime
import unittest

from zambretti_stfn.zambretti import PressureData, Trend, Zambretti


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

    def test_checking_pressure_difference_falling(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1050.5),
                (now - datetime.timedelta(hours=2, minutes=49), 1040.0),
                (now - datetime.timedelta(hours=2, minutes=39), 1030.0),
                (now - datetime.timedelta(hours=2, minutes=12), 1020.0),
                (now - datetime.timedelta(hours=1, minutes=19), 1010.0),
                (now - datetime.timedelta(minutes=20), 1000.0),
            ]
        )
        zambretti = Zambretti()

        assert zambretti._check_pressure_difference(pressure_data) == -50.5

    def test_checking_pressure_difference_rising(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1045),
                (now - datetime.timedelta(hours=2, minutes=49), 1050.50),
                (now - datetime.timedelta(hours=2, minutes=39), 1060.40),
                (now - datetime.timedelta(hours=2, minutes=12), 1070.30),
                (now - datetime.timedelta(hours=1, minutes=19), 1080.20),
                (now - datetime.timedelta(minutes=20), 1090),
            ]
        )
        zambretti = Zambretti()

        assert zambretti._check_pressure_difference(pressure_data) == 45

    def test_calculating_trend_falling(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1002),
                (now - datetime.timedelta(hours=2, minutes=49), 1001),
                (now - datetime.timedelta(hours=2, minutes=39), 1000.90),
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
