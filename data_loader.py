import os
import ssl
import urllib.request
import zipfile
import pandas as pd

from station_manager import StationManager
from planner import JourneyPlanner
from datetime import datetime


class GTFSData:
    def __init__(self):
        self.data_dir = "gtfs_data"
        self.download_and_extract()

        print("Lade Dateien in den Speicher...")

        # Smartes Finden des Ordners
        actual_dir = self.data_dir
        for root, dirs, files in os.walk(self.data_dir):
            if "stops.txt" in files:
                actual_dir = root
                break

        # Jetzt bezieht Pandas die Daten aus dem richtigen Ordner
        self.stops = pd.read_csv(f"{actual_dir}/stops.txt", dtype=str)
        self.stop_times = pd.read_csv(f"{actual_dir}/stop_times.txt", dtype=str)
        self.trips = pd.read_csv(f"{actual_dir}/trips.txt", dtype=str)

        # Jetzt bezieht Pandas die Daten aus dem richtigen Ordner
        self.stops = pd.read_csv(f"{actual_dir}/stops.txt", dtype=str)
        self.stop_times = pd.read_csv(f"{actual_dir}/stop_times.txt", dtype=str)
        self.trips = pd.read_csv(f"{actual_dir}/trips.txt", dtype=str)

        #

        # ========================================

    def download_and_extract(self):
        # 1. Cache-Prüfung
        is_cached = False
        if os.path.exists(self.data_dir):
            for root, dirs, files in os.walk(self.data_dir):
                if "stops.txt" in files:
                    is_cached = True
                    break

        if is_cached:
            print("✅ Daten sind bereits im Cache.")
            return

        print("🌐Lade ZVV GTFS-Daten herunter...")
        os.makedirs(self.data_dir, exist_ok=True)

        url = "https://github.com/olenarudnytskaa/SBB/releases/download/v2.0/sbb_data.zip"
        zip_path = f"{self.data_dir}/zvv_gtfs.zip"

        # 2. УМНАЯ ЗАГРУЗКА БЕЗ СТАРЫХ ФУНКЦИЙ
        import ssl
        import urllib.request

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())

        # 3. Распаковка
        print("📦 Entpacke ZIP-Datei...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.data_dir)

        os.remove(zip_path)
        print("✅ Daten erfolgreich geladen!")





