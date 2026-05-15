import unittest
import pandas as pd
from planner import JourneyPlanner


class DummyGTFS:
    """Ein einfaches Mock-Objekt, um den Planner ohne echte Downloads zu testen."""

    def __init__(self):
        self.stop_times = pd.DataFrame(columns=[
            "trip_id", "stop_id", "stop_sequence", "departure_time", "arrival_time"
        ])


class MockStationManager:
    """Simuliert den StationManager fuer isolierte Tests der Logik."""

    def get_main_stop(self, name):
        return "8503000"

    def get_platforms(self, parent_id):
        return ["8503000:0:1", "8503000:0:2"]


class TestJourneyPlanner(unittest.TestCase):
    def setUp(self):
        # Wird vor jedem Test ausgefuehrt
        dummy_gtfs = DummyGTFS()
        mock_station_manager = MockStationManager()
        self.planner = JourneyPlanner(dummy_gtfs, station_manager=mock_station_manager)

    def test_time_to_minutes(self):
        # Testet die Umwandlung von HH:MM:SS in Minuten
        self.assertEqual(self.planner.time_to_minutes("14:30:00"), 870)
        self.assertEqual(self.planner.time_to_minutes("00:00:00"), 0)
        self.assertEqual(self.planner.time_to_minutes("01:15:00"), 75)

    def test_calculate_duration(self):
        # Testet die Berechnung der Reisedauer
        self.assertEqual(self.planner.calculate_duration("14:00:00", "15:30:00"), 90)
        self.assertEqual(self.planner.calculate_duration("08:15:00", "08:20:00"), 5)

    def test_find_direct_connections_empty(self):
        # Testet das Verhalten, wenn keine Verbindungen existieren
        result = self.planner.find_direct_connections("Zuerich", "Bern", min_time=0)
        self.assertEqual(result, [])

    def test_get_platform_info_unknown(self):
        # Testet den Fallback, wenn das Gleis in den Daten nicht gefunden wird
        platform = self.planner.get_platform_info("trip_999", "Zuerich", "arrival")
        self.assertEqual(platform, "Gleis unbekannt")


if __name__ == '__main__':
    unittest.main()