from datetime import datetime


class JourneyPlanner:
    def __init__(self, gtfs_data, station_manager):
        self.stop_times = gtfs_data.stop_times
        self.station_manager = station_manager
        self.grouped_trips = self.stop_times.groupby("trip_id")

    # AKTUALISIERT: Zeitfilter (min_time) hinzugefügt + Gleis-Info
    def find_direct_connections(self, start_name: str, end_name: str, min_time=0):
        start_parent = self.station_manager.get_main_stop(start_name)
        end_parent = self.station_manager.get_main_stop(end_name)

        start_platforms = set(self.station_manager.get_platforms(start_parent))
        end_platforms = set(self.station_manager.get_platforms(end_parent))

        grouped = self.grouped_trips
        connections = []

        for trip_id, group in grouped:
            trip_stops = group["stop_id"].values

            start_matches = [s for s in trip_stops if s in start_platforms]
            end_matches = [s for s in trip_stops if s in end_platforms]
            if len(start_matches) == 0 or len(end_matches) == 0:
                continue

            start_stop = start_matches[0]
            end_stop = end_matches[0]

            start_seq = int(group[group["stop_id"] == start_stop]["stop_sequence"].iloc[0])
            end_seq = int(group[group["stop_id"] == end_stop]["stop_sequence"].iloc[0])

            if start_seq < end_seq:
                departure = group[group["stop_id"] == start_stop]["departure_time"].iloc[0]
                arrival = group[group["stop_id"] == end_stop]["arrival_time"].iloc[0]

                dep_mins = self.time_to_minutes(departure)

                # НОВОЕ: Достаем номер платформы из ID (Gleis extrahieren)
                dep_platform = f"Gleis {start_stop.split(':')[-1]}" if ":" in start_stop else "Hauptperron"
                arr_platform = f"Gleis {end_stop.split(':')[-1]}" if ":" in end_stop else "Hauptperron"

                # Wir berücksichtigen nur Züge, die SPÄTER als die angegebene Zeit abfahren
                if dep_mins >= min_time:
                    connections.append({
                        "trip_id": trip_id,
                        "departure": departure,
                        "arrival": arrival,
                        "dep_mins": dep_mins,
                        "dep_platform": dep_platform,
                        "arr_platform": arr_platform
                    })

        # Sortieren: zuerst die nächsten Züge
        return sorted(connections, key=lambda x: x["dep_mins"])

    def time_to_minutes(self, time: str):
        h, m, s = map(int, time.split(":"))
        return h * 60 + m

    def calculate_duration(self, departure, arrival):
        return self.time_to_minutes(arrival) - self.time_to_minutes(departure)

    def print_connections(self, connections, start_name, end_name):
        print(f"\n--- DIREKTVERBINDUNGEN: {start_name} -> {end_name} ---")
        for c in connections[:3]:
            duration = self.calculate_duration(c["departure"], c["arrival"])
            # НОВОЕ: Красивый вывод с платформами (Schöne Ausgabe mit Gleisen)
            print(f"Abfahrt: {c['departure']} [{c['dep_platform']}]  ->  Ankunft: {c['arrival']} [{c['arr_platform']}] | Dauer: {duration} Min.")
        print("-" * 50)

    # Intelligente Suche nach Umsteigeverbindungen nach Uhrzeit
    # Intelligente Suche nach Umsteigeverbindungen nach Uhrzeit
    def find_transfer_connections(self, start_name, end_name, transfer_city_name, current_mins, mobility_type="normal"):
        mobility_buffer = {"slow": 15, "normal": 8, "fast": 4}
        min_transfer_time = mobility_buffer.get(mobility_type, 8)

        first_leg = self.find_direct_connections(start_name, transfer_city_name, min_time=current_mins)
        if not first_leg:
            return []

        complex_routes = []
        trip_a = first_leg[0]
        arr_time_a = self.time_to_minutes(trip_a["arrival"])

        second_leg = self.find_direct_connections(
            transfer_city_name,
            end_name,
            min_time=(arr_time_a + min_transfer_time)
        )

        if second_leg:
            trip_b = second_leg[0]
            dep_time_b = self.time_to_minutes(trip_b["departure"])

            arrival_platform = self.get_platform_info(trip_a["trip_id"], transfer_city_name, "arrival")
            departure_platform = self.get_platform_info(trip_b["trip_id"], transfer_city_name, "departure")

            # НОВОЕ: Платформа старта и финиша (Neue: Start- und Zielgleise)
            start_platform = self.get_platform_info(trip_a["trip_id"], start_name, "departure")
            final_arrival_platform = self.get_platform_info(trip_b["trip_id"], end_name, "arrival")

            complex_routes.append({
                "first_trip": trip_a,
                "second_trip": trip_b,
                "transfer_point": transfer_city_name,
                "arrival_platform": arrival_platform,
                "departure_platform": departure_platform,
                "start_platform": start_platform,  # Сохраняем платформу старта
                "final_arrival_platform": final_arrival_platform,  # Сохраняем платформу финиша
                "wait_time": dep_time_b - arr_time_a
            })

        return complex_routes

    def print_transfer_route(self, route, start_name, end_name):
        print(f"\n--- VERBINDUNG MIT UMSTIEG IN {route['transfer_point']} ---")

        # Первая часть пути (Erster Teil der Reise)
        print(f"1. Teil: {start_name.capitalize()} -> {route['transfer_point']}")
        print(f"   Zeit: {route['first_trip']['departure']} -> {route['first_trip']['arrival']}")
        print(f"   Abfahrt von: {route['start_platform']}")  # НОВОЕ: Откуда выезжаем
        print(f"   Ankunft auf: {route['arrival_platform']}")

        print(f"\n   Umsteigen: {route['wait_time']}  (Min.) Zeit 🚶‍♂️💨")

        # Вторая часть пути (Zweiter Teil der Reise)
        print(f"\n2. Teil: {route['transfer_point']} -> {end_name.capitalize()}")
        print(f"   Zeit: {route['second_trip']['departure']} -> {route['second_trip']['arrival']}")
        print(f"   Abfahrt von: {route['departure_platform']}")
        print(f"   Ankunft auf: {route['final_arrival_platform']}")  # НОВОЕ: Куда приезжаем
        print("-" * 50)

    def get_platform_info(self, trip_id, station_name, type="arrival"):
        parent_id = self.station_manager.get_main_stop(station_name)
        platforms = self.station_manager.get_platforms(parent_id)
        trip_stops = self.stop_times[self.stop_times["trip_id"] == trip_id]

        mask = trip_stops["stop_id"].isin(platforms)
        if not mask.any(): return "Gleis unbekannt"

        specific_stop_id = trip_stops[mask].iloc[0]["stop_id"]
        if ":" in specific_stop_id: return f"Gleis {specific_stop_id.split(':')[-1]}"
        return "Hauptperron"



    # НОВОЕ: Симуляция экрана в поезде (Zug-Bildschirm Simulation)
    def simulate_display(self, route, end_name):
        wait_time = route['wait_time']
        if wait_time <= 5:
            label = "🔴 CRITICAL (Kritisch) - Nur für Sprinter!"
        elif wait_time <= 8:
            label = "🟠 TIGHT (Knapp) - Zügig umsteigen"
        else:
            label = "🟢 COMFORTABLE (Entspannt) - Genug Zeit"

        print("\n" + "═" * 60)
        print("📺 ZUG-BILDSCHIRM")
        print("═" * 60)
        print(f"📍 Nächster Halt: {route['transfer_point']}")
        print(f"🕒 Ankunft: {route['first_trip']['arrival']} | {route['arrival_platform']}")
        print("─" * 60)
        print("🔗 ANSCHLÜSSE:")
        print(f"🚆 Richtung: {end_name.capitalize()}")
        print(f"🕒 Abfahrt: {route['second_trip']['departure']} | {route['departure_platform']}")
        print(f"⏳ Umsteigezeit: {wait_time} мин (Min.)")
        print(f"⚠️ Status: {label}")
        print("═" * 60 + "\n")

    def smart_routing(self, start_name, end_name, start_mins, target_date, mobility_type="normal"):
        hh = start_mins // 60
        mm = start_mins % 60
        print(f"\n📅 Reisedatum: {target_date}")
        print(f"🕒 Abfahrtszeit: {hh:02d}:{mm:02d}")
        print("Fahrplan wird analysiert...")

        direct = self.find_direct_connections(start_name, end_name, min_time=start_mins)
        if direct:
            print("✅ Direktverbindung gefunden!")
            self.print_connections(direct, start_name, end_name)
            return

        print("🔄 Suche Umsteigeverbindungen...")
        hubs = ["Zürich HB", "Winterthur", "Bern", "Olten", "Basel SBB", "Luzern"]

        for hub in hubs:
            if hub.lower() in [start_name.lower(), end_name.lower()]:
                continue

            routes = self.find_transfer_connections(start_name, end_name, hub, start_mins, mobility_type)
            if routes:
                print(f"✅ Route gefunden!")
                self.print_transfer_route(routes[0], start_name, end_name)
                self.simulate_display(routes[0], end_name)
                return

        print("❌ Keine Route gefunden.")





