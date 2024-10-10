from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

import psycopg2
import datetime
from dateutil import parser

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
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
        
        activity_data = client.get_stats(end_date.isoformat())
        user_profile_id = activity_data.get('userProfileId', [])
        
        create_users_table()
        register_user(email, password, user_profile_id)
        
        
        create_heartrate_table()
        #for date in date_range:
        heart_rate_data = client.get_heart_rates(start_date.isoformat())
        data = heart_rate_data.get('heartRateValues', [])
            
        if heart_rate_data is not None:
                data = heart_rate_data.get('heartRateValues', [])
                for record in data:
                    if len(record) == 2:
                        timestamp = record[0]
                        heartrate = record[1]
                        save_heart_rate_data(timestamp, heartrate, user_profile_id)
                    else:
                        print(f"Nem várt formátum: {record}")
        else:
                print(f"Nem érkezett adat.")
    
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
    
