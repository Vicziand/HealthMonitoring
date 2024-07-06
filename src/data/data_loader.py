from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

import datetime
from dateutil import parser
import db_utils

# Bejelentkezési adatok
email = "vicziand@gmail.com"
password = "H3althM0n"

def iso_to_unix_timestamp(iso_str):
    dt = parser.isoparse(iso_str)
    return int(dt.timestamp() * 1000)

try:
    client = Garmin(email, password)
    client.login()

    start_date = datetime.date(2024, 6, 21)
    end_date = datetime.date.today()
    date_range = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    
    conn = db_utils.db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT timestamp::date FROM sleep_data")
    existing_dates = {record[0] for record in cur.fetchall()}
    
    min_heart_rate = 30
    max_heart_rate = 200  

    for single_date in date_range:
        if single_date not in existing_dates:  # Csak a még nem feldolgozott napok adatait dolgozza fel
            sleep_data = client.get_sleep_data(single_date.isoformat())
        #print(sleep_data)
    
            if 'wellnessEpochRespirationDataDTOList' in sleep_data and 'sleepHeartRate' in sleep_data:
                sleep_heart_rate_data = sleep_data.get('sleepHeartRate', [])
                respiration_data = sleep_data.get('wellnessEpochRespirationDataDTOList',[])
                sleep_movement_data = sleep_data.get('sleepMovement', [])
                sleep_spo2_data = sleep_data.get('wellnessEpochSPO2DataDTOList', [])

                # Egy dictionary-t hozunk létre a sleepHeartRate adatokhoz, hogy gyorsabban tudjunk keresni
                respiration_data_dict = {record['startTimeGMT']: record['respirationValue'] for record in respiration_data}
                #heart_rate_dict = {record['startGMT']: record['value'] for record in sleep_heart_rate_data}
                movement_dict = {iso_to_unix_timestamp(record['startGMT']): record['activityLevel'] for record in sleep_movement_data}
                spo2_dict = {iso_to_unix_timestamp(record['epochTimestamp']): (record['spo2Reading'], record['readingConfidence']) for record in sleep_spo2_data}

                for record in sleep_heart_rate_data:
                    timestamp = record.get('startGMT')
                    sleep_heart_rate = record.get('value')
                    
                    #Adat tisztítás. Kiszűri a kiugró pulzus értékeket,amik valószínűsíthetően mérési hibából adóthatnak. 
                    if not (min_heart_rate <= sleep_heart_rate <= max_heart_rate):
                        continue
                    
                    respiration_value = respiration_data_dict.get(timestamp)
                    activity_level = movement_dict.get(timestamp) 
                    spo2_reading, reading_confidence = spo2_dict.get(timestamp, (None, None))
                    #print(f"Timestamp: {timestamp}, Respiration Value: {respiration_value}, Sleep Heart Rate: {sleep_heart_rate}, Activity Level: {activity_level}, SPO2: {spo2_reading}, Reading Confidence: {reading_confidence}")
                
                    postgres_timestamp = datetime.datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')
                    
                    #Adat tisztítás betöltés előtt:
                    # Ha az adott timestamp érték már létezik az adatbázisban, akkor frissíti új értékkel a rekordot, nem hoz létre újat.
                    # 
                    cur.execute("""
                        INSERT INTO sleep_data (timestamp, sleepHeartRate, activityLevel, spo2Reading, readingConfidence, respirationValue)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (timestamp) DO UPDATE SET
                            sleepHeartRate = EXCLUDED.sleepHeartRate,
                            activityLevel = EXCLUDED.activityLevel,
                            spo2Reading = EXCLUDED.spo2Reading,
                            readingConfidence = EXCLUDED.readingConfidence,
                            respirationValue = EXCLUDED.respirationValue
                    """, (postgres_timestamp, sleep_heart_rate, activity_level, spo2_reading, reading_confidence, respiration_value))

    conn.commit()
    
except (
    GarminConnectConnectionError,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
) as err:
    print(f"Hiba történt: {err}")

except Exception as e:
    print(f"Hiba történt: {e}")

finally:
    print("Sikeres az adatok mentése az adatbázisba!")
    if cur:
        cur.close()
    if conn:
        conn.close()
    