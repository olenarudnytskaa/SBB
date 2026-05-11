import pandas as pd

class StationManager:
    def __init__(self, gfts_data):
        self.stops = gfts_data.stops
        self.stop_name_map = dict(zip(self.stops["stop_id"], self.stops["stop_name"]))


    def find_stop_id(self, name):
        result = self.stops[self.stops["stop_name"].str.lower() == name.lower()]
        return result[["stop_id", "stop_name"]]

    def get_main_stop(self, name):
        results = self.stops[self.stops["stop_name"].str.lower() == name.lower()]
        if len(results) == 0:
            raise Exception(f"Station nicht gefunden: {name}")

        numeric = results[results["stop_id"].str.match(r"^\d+$")]
        if len(numeric) > 0:
            return numeric.iloc[0]["stop_id"]

        for sid in results["stop_id"]:
            if "Parent" in sid:
                return sid.replace("Parent", "")

        sid = results.iloc[0]["stop_id"]
        return sid.split(":")[0]

    def get_main_stop(self, name):
        # 1. Wörterbuch der intelligenten Ersetzungen (Alias-Wörterbuch für Smart Defaults)
        # Wenn der Benutzer einen Schlüssel eingegeben hat (links), suchen wir nach dem Wert (rechts)
        aliases = {
            "zürich": "Zürich HB",
            "zurich": "Zürich HB",
            "basel": "Basel SBB",
            "bern": "Bern",
            "luzern": "Luzern",
            "genf": "Genève",
            "geneve": "Genève",
            "winterthur": "Winterthur"
        }

        # Wir ändern den Namen, sofern er im Wörterbuch enthalten ist. Andernfalls behalten wir die eingegebene Bezeichnung bei.
        search_name = aliases.get(name.lower().strip(), name.strip())

        # 2. Wir suchen nach einer Station in der Datenbank
        results = self.stops[self.stops["stop_name"].str.lower() == search_name.lower()]

        if len(results) == 0:
            # Wir geben eine verständlichere Fehlermeldung aus
            raise Exception(f"Station nicht gefunden: '{name}' (Ich habe in der Datenbank gesuchtи: '{search_name}')")

        # numerische Haupt-ID suchen
        numeric = results[results["stop_id"].str.match(r"^\d+$")]
        if len(numeric) > 0:
            return numeric.iloc[0]["stop_id"]

        # Parent ID finden (Wollen ja den ganzen Bahnhof)
        for sid in results["stop_id"]:
            if "Parent" in sid:
                return sid.replace("Parent", "")

                # Fallback
        sid = results.iloc[0]["stop_id"]
        return sid.split(":")[0]

    def get_platforms(self, parent_id):
        return self.stops[self.stops["stop_id"].str.startswith(parent_id + ":")]["stop_id"].values

    def get_stop_name(self, stop_id):
        return self.stop_name_map.get(stop_id, "Unknown")
