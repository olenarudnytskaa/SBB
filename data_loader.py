import os
import ssl
import urllib.request
import zipfile
import pandas as pd
import sys


class GTFSData:
    def __init__(self):
        self.data_dir = "gtfs_data"

        # 1. Robustheit: Internet/Download
        try:
            self.download_and_extract()
        except Exception as e:
            print(f"\nKRITISCHER DOWNLOAD-FEHLER: {e}")
            print(
                "Bitte ueberpruefen Sie Ihre Internetverbindung. Das Programm kann ohne Daten nicht ausgefuehrt werden.")
            sys.exit(1)

        print("Lade Dateien in den Speicher...")

        # 2. Robustheit: Dateisystem
        actual_dir = None
        for root, dirs, files in os.walk(self.data_dir):
            if "stops.txt" in files:
                actual_dir = root
                break

        if not actual_dir:
            print("FEHLER: Fahrplandateien (GTFS) wurden im Archiv nicht gefunden.")
            sys.exit(1)

        # 3. Robustheit: Pandas/CSV
        try:
            self.stops = pd.read_csv(f"{actual_dir}/stops.txt", dtype=str)
            self.stop_times = pd.read_csv(f"{actual_dir}/stop_times.txt", dtype=str)
            self.trips = pd.read_csv(f"{actual_dir}/trips.txt", dtype=str)
            print("Alle Daten erfolgreich geladen.")
        except Exception as e:
            print(f"FEHLER beim Lesen der CSV-Dateien: {e}")
            sys.exit(1)

    def download_and_extract(self):
        # Cache-Pruefung
        is_cached = False
        if os.path.exists(self.data_dir):
            for root, dirs, files in os.walk(self.data_dir):
                if "stops.txt" in files:
                    is_cached = True
                    break

        if is_cached:
            print("Daten sind bereits im Cache.")
            return

        print("Lade SBB GTFS-Daten herunter...")
        os.makedirs(self.data_dir, exist_ok=True)

        url = "https://github.com/olenarudnytskaa/SBB/releases/download/v2.0/sbb_data.zip"
        zip_path = f"{self.data_dir}/sbb_data.zip"

        # Absicherung der Netzwerkanfrage
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=20) as response, open(zip_path, 'wb') as out_file:
                out_file.write(response.read())
        except urllib.error.URLError as e:
            raise Exception(f"Keine Verbindung zum Server moeglich: {e}")

        # Absicherung beim Entpacken der ZIP-Datei
        print("Entpacke ZIP-Datei...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
        except zipfile.BadZipFile:
            raise Exception("ZIP-Datei ist beschaedigt oder hat ein ungueltiges Format.")
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

        print("Daten erfolgreich geladen!")


