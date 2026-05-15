from datetime import datetime
from data_loader import GTFSData
from station_manager import StationManager
from planner import JourneyPlanner


def main():
    print("======================================")
    print(" SBB  🇨🇭")
    print("======================================")

    # 1. Daten laden
    gtfs_data = GTFSData()
    station_manager = StationManager(gtfs_data)
    planner = JourneyPlanner(gtfs_data, station_manager)

    # 2. Benutzereingabe
    start_name = input("Von: ")
    end_name = input("Nach: ")

    # Intelligente Datumsprüfung
    while True:
        target_date = input("Reisedatum DD.MM.YYYY): ")
        if not target_date:
            target_date = datetime.now().strftime("%d.%m.%Y")
            break
        try:

            valid_date = datetime.strptime(target_date, "%d.%m.%Y")
            target_date = valid_date.strftime("%d.%m.%Y")
            break
        except ValueError:
            print("⚠️ Fehler: Ungültiges Datum.")

    # Intelligente Zeitprüfung
    while True:
        start_time_str = input("Abfahrtszeit HH:MM: ")
        if not start_time_str:
            now = datetime.now()
            start_mins = now.hour * 60 + now.minute
            break
        try:
            hh, mm = map(int, start_time_str.split(":"))
            if 0 <= hh <= 23 and 0 <= mm <= 59:
                start_mins = hh * 60 + mm
                break
            else:
                print("⚠️ Fehler: Ungültige Zeit.")
        except ValueError:
            print("⚠️ Fehler: Format HH:MM.")

    # Mobilitätswahl
    print("\nWie möchten Sie reisen?")
    print("1 - Bequem 15 Minuten")
    print("2 - Standard 8 Minuten)")
    print("3 - Speed 4 Minuten")

    choice = input("Wählen Sie 1, 2 oder 3: ")

    mobility = "normal"
    if choice == "1":
        mobility = "slow"
        print("-> Bequemer Modus ausgewählt.")
    elif choice == "3":
        mobility = "fast"
        print("->Schneller Modus ausgewählt.")
    else:
        print("-> Standardmodus ausgewählt.")

    # 3. Planer starten
    planner.smart_routing(start_name, end_name, start_mins, target_date, mobility_type=mobility)





if __name__ == "__main__":
    main()