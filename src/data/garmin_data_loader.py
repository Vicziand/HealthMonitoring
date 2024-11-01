from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

import datetime
from dateutil import parser

import os
import sys
# A könyvtár relatív elérési útja
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data.db_utils import *

# Bejelentkezési adatok
#email = "vicziand@gmail.com"
#password = "H3althM0n"
#email = "cs.viczian@gmail.com"
#password = "Garmin12"

def garmin_login(email, password):
    try:
        client = Garmin(email, password)
        client.login()
    
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)
        date_range = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        
        # Felhasználói adatok lekérése és regisztrálása
        activity_data = client.get_stats(end_date.isoformat())
        if not activity_data:
            print("Nem sikerült felhasználói adatokat lekérni.")
            return False

        user_profile_id = activity_data.get('userProfileId', None)
        if not user_profile_id:
            print("Nem sikerült userProfileId-t lekérni.")
            return False

        # Felhasználói tábla létrehozása és felhasználó regisztrációja
        create_users_table()
        register_user(email, password, user_profile_id)
        
        # Szívritmus adatok táblájának létrehozása
        create_heartrate_table()

        # Szívritmus adatok lekérése minden napra külön
        for date in date_range:
            heart_rate_data = client.get_heart_rates(date.isoformat())
            if heart_rate_data:
                data = heart_rate_data.get('heartRateValues', [])
                if data:  # Ellenőrizzük, hogy van-e adat
                    for record in data:
                        if len(record) == 2:
                            timestamp = record[0]
                            heartrate = record[1]
                            # Csak akkor mentjük, ha a szívritmus adat nem None
                            if timestamp is not None and heartrate is not None:
                                save_heart_rate_data(timestamp, heartrate, user_profile_id)
                            else:
                                print(f"Hiányos szívritmus adat: {record}")
                        else:
                            print(f"Nem várt formátum: {record}")
            else:
                print(f"Nincs szívritmus adat a következő napra: {date.isoformat()}")
        
        # Tevékenységek és alvási adatok táblájának létrehozása
        create_activities_table()

        # Tevékenységek és alvási adatok lekérése minden napra külön
        for date in date_range:
            sleep_data = client.get_sleep_data(date.isoformat())
            activity_data = client.get_stats(date.isoformat())
            
            if not activity_data:
                print(f"Nincs tevékenységi adat a következő napra: {date.isoformat()}")
                continue

            userProfileId = activity_data.get('userProfileId', None)
            totalSteps = activity_data.get('totalSteps', None)
            averageStressLevel = activity_data.get('averageStressLevel', None)
            sleepingSeconds = activity_data.get('sleepingSeconds', None)
            activeSeconds = activity_data.get('activeSeconds', None)
            
            # Alvás minőségének lekérése, ha elérhető
            sleepQuality = None
            if sleep_data and 'dailySleepDTO' in sleep_data and 'sleepScores' in sleep_data['dailySleepDTO']:
                sleepQuality = sleep_data['dailySleepDTO']['sleepScores']['overall'].get('value', None)
                
            calendar_date_str = activity_data.get('calendarDate', None)
            calendarDate = None
            if calendar_date_str:
                try:
                    calendarDate = datetime.datetime.strptime(calendar_date_str, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Hibás dátumformátum: {calendar_date_str}")
                    continue
            else:
                print(f"Nincs érvényes calendarDate a következő napra: {date.isoformat()}")
                continue
            
            # Csak akkor mentjük az adatokat, ha minden szükséges adat rendelkezésre áll
            if all(value is not None for value in [userProfileId, totalSteps, averageStressLevel, sleepingSeconds, activeSeconds, sleepQuality, calendarDate]):
                save_activities_data(totalSteps, averageStressLevel, sleepingSeconds, activeSeconds, sleepQuality, userProfileId, calendarDate)
            else:
                print(f"Hiányos adatok a következő napra: {date.isoformat()}")
        
        return True
    
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print(f"Hiba történt: {err}")

    except Exception as e:
        print(f"Ismeretlen hiba történt: {e}")
    
    return False