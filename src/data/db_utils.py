import psycopg2
from sqlalchemy import create_engine
#SQLAlchemy egy python csomag, ami sql adatbázis kapcsolat létrehozására szolgál
import pandas as pd
#A Pandas egy Python könyvtár, ami adatok feldolgozására és elemzésére szolgál.
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib
import os

db_config = st.secrets["database"]

def db_connection():
    return psycopg2.connect(
        dbname=db_config["name"],
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"]
    )
    
def sql_engine():
    return create_engine(
        f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["name"]}'
    )

def fetch_data(query):
    engine = sql_engine()
    return pd.read_sql(query, engine)

def create_chd_table():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chd (
            id SERIAL PRIMARY KEY,
            male INTEGER,
            age INTEGER,
            cigsperday INTEGER,
            bpmeds INTEGER,
            prevalentstroke INTEGER,
            prevalenthyp INTEGER,
            diabetes INTEGER,
            heartrate INTEGER,
            bmi FLOAT,
            tenyearchd INTEGER
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    
def clear_chd_table():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chd;")
    conn.commit()
    cur.close()
    conn.close()

def data_clean_chd():
    Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")
    
    data_clean = Rawdata.copy()

    # Hiányzó értékek kitöltése a 'BPMeds' oszlopban a leggyakoribb értékkel
    si_freq = SimpleImputer(strategy='most_frequent')
    data_clean['BPMeds'] = si_freq.fit_transform(Rawdata[['BPMeds']])
    data_clean['education'] = si_freq.fit_transform(Rawdata[['education']])
    # A maradék oszlopok kitöltése átlaggal (kivéve a 'BPMeds' és 'education' oszlopokat)
    remaining_columns = data_clean.columns.difference(['BPMeds', 'education'])
    si_mean = SimpleImputer(strategy='median')
    data_clean[remaining_columns] = pd.DataFrame(si_mean.fit_transform(data_clean[remaining_columns]), 
                                                 columns=remaining_columns, 
                                                 index=data_clean.index)
    return data_clean
    

def correlation_chd(data_clean):
    plt.figure(figsize= (16, 8))
    sns.heatmap(data_clean.corr(), annot = True, cmap= 'RdYlBu', fmt= '.2f');
    st.pyplot(plt)

def data_load_chd(data):
    conn = db_connection()
    cur = conn.cursor()
    final_data = data[['male', 'age', 'cigsPerDay', 'BPMeds', 'prevalentStroke', 'prevalentHyp', 'diabetes', 'heartRate', 'BMI', 'TenYearCHD']]
    # Az adatok listává alakítása
    insert_values = [tuple(row) for _, row in final_data.iterrows()]
    # SQL lekérdezés létrehozása az összes sor beszúrására
    values_str = ', '.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row).decode('utf-8') for row in insert_values)
    insert_query = f"""
        INSERT INTO chd (male, age, cigsperday, bpmeds, prevalentstroke, prevalenthyp, diabetes, heartrate, bmi, tenyearchd)
        VALUES {values_str}
    """
    # Lekérdezés végrehajtása
    cur.execute(insert_query)
    
    
    conn.commit()
    cur.close()
    conn.close()
    
def prepare_chd_data():
    create_chd_table()
    clear_chd_table()
    data = data_clean_chd()
    data_load_chd(data)
    
def create_sleep_table():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS sleep(
                id SERIAL PRIMARY KEY,
                gender INTEGER,
                age INTEGER,
                duration FLOAT,
                quality INTEGER,
                activity INTEGER,
                stress INTEGER,
                bmi INTEGER,
                heartrate INTEGER,
                steps INTEGER,
                disorder INTEGER
            );
    """)
    conn.commit()
    cur.close()
    conn.close()
    
def clear_sleep_table():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sleep;")
    conn.commit()
    cur.close()
    conn.close()
    
def data_clean_sleep():
    # Az adat beolvasása
    Rawdata = pd.read_csv("src/data/raw/training_data_sleep.csv")

    # Csak a szükséges oszlopok kiválasztása és másolat készítése
    data = Rawdata[['Gender', 'Age', 'Sleep Duration', 'Quality of Sleep', 'Physical Activity Level', 
                    'Stress Level', 'BMI Category', 'Heart Rate', 'Daily Steps', 'Sleep Disorder']].copy()

    # Hiányzó értékek kezelése
    data['Sleep Disorder'].fillna('None', inplace=True)
    data['BMI Category'] = data['BMI Category'].replace({'Normal Weight': 'Normal'})

    # Encoderek
    label_encoder_gender = LabelEncoder()
    encoder_disorder = OrdinalEncoder(categories=[['None', 'Sleep Apnea', 'Insomnia']])
    encoder_bmi = OrdinalEncoder(categories=[['Normal', 'Overweight', 'Obese']])
    data['gender'] = label_encoder_gender.fit_transform(data['Gender'])
    # Az encoderek alkalmazása
    data['disorder'] = encoder_disorder.fit_transform(data[['Sleep Disorder']])
    data['bmi'] = encoder_bmi.fit_transform(data[['BMI Category']])
    data['gender'] = label_encoder_gender.fit_transform(data['Gender'])
    
    numeric_data = data.drop(columns=['Gender', 'BMI Category', 'Sleep Disorder'])

    return numeric_data

def data_load_sleep(data):
    conn = db_connection()
    cur = conn.cursor()
    data['gender'] = data['gender'].astype(float)
    data['Age'] = data['Age'].astype(float)
    data['Sleep Duration'] = data['Sleep Duration'].astype(float)
    data['Quality of Sleep'] = data['Quality of Sleep'].astype(float)
    data['Physical Activity Level'] = data['Physical Activity Level'].astype(float)
    data['Stress Level'] = data['Stress Level'].astype(float)
    data['bmi'] = data['bmi'].astype(float)
    data['Heart Rate'] = data['Heart Rate'].astype(float)
    data['Daily Steps'] = data['Daily Steps'].astype(float)

    # Minden sor beszúrása a táblába
    insert_query = """
        INSERT INTO sleep (gender, age, duration, quality, activity, 
        stress, bmi, heartrate, steps, disorder)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    insert_values = data[['gender', 'Age', 'Sleep Duration', 'Quality of Sleep', 
                      'Physical Activity Level', 'Stress Level', 'bmi', 'Heart Rate',
                      'Daily Steps', 'disorder']].values.tolist()
    
    cur.executemany(insert_query, insert_values)  
    conn.commit()
    cur.close()
    conn.close()
    
def prepare_sleep_data():
    create_sleep_table()
    clear_sleep_table()
    data = data_clean_sleep()
    data_load_sleep(data)
    
def create_users_table():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        userProfileId BIGINT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def hash_password(password):
    # 16 byte véletlenszerű só generálása
    salt = os.urandom(16)
    # A jelszó hash-elése a salt használatával
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # A só és a hash együttes visszaadása
    return salt + hashed_password
    
def register_user(email, password, user_profile_id):
    conn = db_connection()
    cur = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cur.execute("INSERT INTO users (email, password_hash, userProfileId) VALUES (%s, %s, %s)", (email, hashed_password, user_profile_id))
        conn.commit()
    except psycopg2.IntegrityError:
        print("Ez az email cím már regisztrálva van.")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
    
    return True

def create_activities_table():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            totalSteps INTEGER,
            averageStressLevel INTEGER,
            sleepingSeconds INTEGER,
            activeSeconds INTEGER,
            sleepQuality INTEGER,
            userProfileId BIGINT NOT NULL,
            calendarDate DATE UNIQUE,
            FOREIGN KEY (userProfileId) REFERENCES users(userProfileId)
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
def create_heartrate_table():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS heartrates (
            id SERIAL PRIMARY KEY,
            timestamp BIGINT,
            heartrate INTEGER,
            userProfileId BIGINT NOT NULL,
            FOREIGN KEY (userProfileId) REFERENCES users(userProfileId)
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def save_heart_rate_data(records):
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.executemany("INSERT INTO heartrates (timestamp, heartrate, userProfileId) VALUES (%s, %s, %s)",
                 records)
        
        conn.commit()
    except Exception as e:
        print(f"Hiba történt az adat mentésekor: {e}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()

def save_activities_data(records):
    conn = db_connection()
    cur = conn.cursor()
    
    try:
        cur.executemany("INSERT INTO activities (totalSteps, averageStressLevel, sleepingSeconds, activeSeconds, sleepQuality, userProfileId, calendarDate) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (calendarDate) DO NOTHING",
                    records)
        conn.commit()
    except Exception as e:
        print(f"Hiba történt az adat mentésekor: {e}")
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()