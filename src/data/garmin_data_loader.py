from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

import datetime
from dateutil import parser
#import db_utils

# Bejelentkezési adatok
email = "vicziand@gmail.com"
password = "H3althM0n"
#email = "cs.viczian@gmail.com"
#password = "Garmin12"

try:
    client = Garmin(email, password)
    client.login()
    
    date = datetime.date(2024, 10, 1)
    heart_rate_data = client.get_heart_rates(date.isoformat())
    name = client.get_full_name()
    activity_data = client.get_stats(date.isoformat())
    activities = client.get_activities(0,1)
    sleep_data = client.get_sleep_data(date.isoformat())
    
    print(activity_data)
    
except (
    GarminConnectConnectionError,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
) as err:
    print(f"Hiba történt: {err}")

except Exception as e:
    print(f"Ismeretlen hiba történt: {e}")