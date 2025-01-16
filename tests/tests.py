import csv
import datetime
import tempfile
import unittest

from zambretti_py.zambretti import PressureData, Trend, WindDirection, Zambretti


class TestLoadingGenericCSVFile(unittest.TestCase):
    def test_loading_csv_happy_path(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(tmpdirname + "history.csv", "w", newline="") as csvfile:
                history = csv.writer(csvfile, delimiter=",")
                history.writerow(["state", "last_changed"])
                history.writerow(["988.6", "2024-11-19T11:33:32.706Z"])
                history.writerow(["988.5", "2024-11-19T11:34:06.863Z"])
                history.writerow(["988.4", "2024-11-19T11:37:06.887Z"])

            pressure_data = PressureData.from_csv_file(
                fname=tmpdirname + "history.csv",
                timestamp_column_position=1,
                pressure_column_position=0,
                skip_header_rows=1,
                strptime_template="%Y-%m-%dT%H:%M:%S.%fZ",
            )

            expected_pd = PressureData(
                points=[
                    (datetime.datetime(2024, 11, 19, 11, 33, 32, 706000), 988.6),
                    (datetime.datetime(2024, 11, 19, 11, 34, 6, 863000), 988.5),
                    (datetime.datetime(2024, 11, 19, 11, 37, 6, 887000), 988.4),
                ]
            )

            self.assertEqual(pressure_data, expected_pd)

    def test_loading_csv_ignores_empty_readings(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(tmpdirname + "history.csv", "w", newline="") as csvfile:
                history = csv.writer(csvfile, delimiter=",")
                history.writerow(["state", "last_changed"])
                history.writerow(["unavailable", "2024-11-19T11:33:32.706Z"])
                history.writerow(["988.5", "2024-11-19T11:34:06.863Z"])
                history.writerow(["988.4", "2024-11-19T11:37:06.887Z"])

            pressure_data = PressureData.from_csv_file(
                fname=tmpdirname + "history.csv",
                timestamp_column_position=1,
                pressure_column_position=0,
                skip_header_rows=1,
                strptime_template="%Y-%m-%dT%H:%M:%S.%fZ",
            )

            expected_pd = PressureData(
                points=[
                    (datetime.datetime(2024, 11, 19, 11, 34, 6, 863000), 988.5),
                    (datetime.datetime(2024, 11, 19, 11, 37, 6, 887000), 988.4),
                ]
            )

            self.assertEqual(pressure_data, expected_pd)


class TestLoadingCSVFromHomeAssistant(unittest.TestCase):
    def test_loading_csv_happy_path(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(tmpdirname + "history.csv", "w", newline="") as csvfile:
                history = csv.writer(csvfile, delimiter=",")
                history.writerow(["entity_id", "state", "last_changed"])
                history.writerow(
                    ["sensor.pressure_2", "988.6", "2024-11-19T11:33:32.706Z"]
                )
                history.writerow(
                    ["sensor.pressure_2", "988.5", "2024-11-19T11:34:06.863Z"]
                )
                history.writerow(
                    ["sensor.pressure_2", "988.4", "2024-11-19T11:37:06.887Z"]
                )

            pressure_data = PressureData.from_home_assistant_csv(
                tmpdirname + "history.csv"
            )

            expected_pd = PressureData(
                points=[
                    (datetime.datetime(2024, 11, 19, 11, 33, 32, 706000), 988.6),
                    (datetime.datetime(2024, 11, 19, 11, 34, 6, 863000), 988.5),
                    (datetime.datetime(2024, 11, 19, 11, 37, 6, 887000), 988.4),
                ]
            )

            self.assertEqual(pressure_data, expected_pd)


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
        assert sea_level_pressure.points[0][1] == 1012.13

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

    def test_forecasting_pressure_falling_quickly(self):
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
        self.assertEqual(forecast, "Showery, Becoming More Unsettled")

    def test_forecasting_pressure_rising(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1001),
                (now - datetime.timedelta(hours=2, minutes=49), 1002),
                (now - datetime.timedelta(hours=2, minutes=39), 1001),
                (now - datetime.timedelta(hours=2, minutes=12), 1000),
                (now - datetime.timedelta(hours=1, minutes=19), 1005),
                (now - datetime.timedelta(minutes=20), 1007),
            ]
        )
        zambretti = Zambretti()

        forecast = zambretti.forecast(
            elevation=90,
            temperature=25,
            pressure_data=pressure_data,
            wind_direction=WindDirection.NORTH,
        )
        self.assertEqual(forecast, "Becoming Fine")

    def test_forecasting_with_high_pressure(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1035),
                (now - datetime.timedelta(hours=2, minutes=59), 1035),
                (now - datetime.timedelta(hours=2, minutes=59), 1035),
                (now - datetime.timedelta(hours=2, minutes=59), 1034),
                (now - datetime.timedelta(hours=2, minutes=59), 1033),
                (now - datetime.timedelta(hours=2, minutes=59), 1033),
                (now - datetime.timedelta(hours=2, minutes=59), 1033),
                (now - datetime.timedelta(hours=2, minutes=59), 1033),
                (now - datetime.timedelta(hours=2, minutes=59), 1031),
                (now - datetime.timedelta(hours=2, minutes=59), 1031),
                (now - datetime.timedelta(hours=2, minutes=49), 1032),
                (now - datetime.timedelta(hours=2, minutes=39), 1032),
                (now - datetime.timedelta(hours=2, minutes=12), 1032),
                (now - datetime.timedelta(hours=1, minutes=19), 1032),
                (now - datetime.timedelta(minutes=20), 1035),
            ]
        )
        zambretti = Zambretti()

        forecast = zambretti.forecast(
            elevation=90,
            temperature=25,
            pressure_data=pressure_data,
            wind_direction=WindDirection.NORTH,
        )
        self.assertEqual(forecast, "Settled Fine")

    def test_forecasting_with_low_pressure(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 971),
                (now - datetime.timedelta(hours=2, minutes=49), 972),
                (now - datetime.timedelta(hours=2, minutes=39), 971),
                (now - datetime.timedelta(hours=2, minutes=12), 970),
                (now - datetime.timedelta(hours=1, minutes=19), 975),
                (now - datetime.timedelta(minutes=20), 977),
                (now - datetime.timedelta(minutes=10), 977),
            ]
        )
        zambretti = Zambretti()

        forecast = zambretti.forecast(
            elevation=90,
            temperature=25,
            pressure_data=pressure_data,
            wind_direction=WindDirection.NORTH,
        )
        self.assertEqual(forecast, "Rather Unsettled, Clearing Later")

    def test_forecasting_with_impossibly_high_pressure(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1071),
                (now - datetime.timedelta(hours=2, minutes=49), 1072),
                (now - datetime.timedelta(hours=2, minutes=39), 1071),
                (now - datetime.timedelta(hours=2, minutes=12), 1070),
                (now - datetime.timedelta(hours=1, minutes=19), 1075),
                (now - datetime.timedelta(minutes=20), 1077),
                (now - datetime.timedelta(minutes=10), 1077),
            ]
        )
        zambretti = Zambretti()

        forecast = zambretti.forecast(
            elevation=90,
            temperature=25,
            pressure_data=pressure_data,
            wind_direction=WindDirection.NORTH,
        )
        self.assertEqual(
            forecast, "Could not determine the pressure trend from available data"
        )

    def test_forecasting_requires_minimum_six_pressure_readings(self):
        now = datetime.datetime.now()
        pressure_data = PressureData(
            [
                (now - datetime.timedelta(hours=2, minutes=59), 1001),
                (now - datetime.timedelta(hours=2, minutes=49), 1002),
            ]
        )
        zambretti = Zambretti()

        with self.assertRaises(ValueError):
            zambretti.forecast(
                elevation=90,
                temperature=25,
                pressure_data=pressure_data,
                wind_direction=WindDirection.NORTH,
            )
