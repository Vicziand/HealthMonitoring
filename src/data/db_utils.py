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
#sns.set_style('darkgrid')
import bcrypt

def db_connection():
    return psycopg2.connect(
        dbname="health_monitor",
        user="postgres",
        password="Healthdb",
        host="localhost"
    )
    
def sql_engine():
    return create_engine('postgresql://postgres:Healthdb@localhost/health_monitor')

def fetch_data(query):
    engine = sql_engine()
    return pd.read_sql(query, engine)
#Az adatbázisból lekérdezett adatokat közvetlenül egy Pandas DataFrame-be töltjük be
#data = Rawdata[['male','age','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','sysBP','diaBP','heartRate','BMI','TenYearCHD']]

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
    #data = Rawdata[['male','age','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']]
    
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
    # Ellenőrzés, hogy sikerült-e a hiányzó adatok kitöltése
    print(data_clean.isnull().sum())
    st.write(data_clean)
    
    return data_clean

def correlation_chd(data_clean):
    plt.figure(figsize= (16, 8))
    sns.heatmap(data_clean.corr(), annot = True, cmap= 'RdYlBu', fmt= '.2f');
    st.pyplot(plt)

def data_load_chd(data):
    
    conn = db_connection()
    cur = conn.cursor()
    final_data = data[['male','age','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']]
    # Minden sor beszúrása a táblába
    for i, row in final_data.iterrows():
        cur.execute("""
            INSERT INTO chd (male, age, cigsperday, bpmeds, 
            prevalentstroke, prevalenthyp, diabetes, heartrate, bmi, tenyearchd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))

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
    Rawdata = pd.read_csv("src/data/raw/training_data_sleep.csv")

    data = Rawdata[['Gender','Age','Sleep Duration','Quality of Sleep','Physical Activity Level','Stress Level','BMI Category','Heart Rate','Daily Steps','Sleep Disorder']]
    data['Sleep Disorder'].fillna('None', inplace=True)
    data['BMI Category']=data['BMI Category'].replace({'Normal Weight':'Normal'})

    label_encoder_gender = LabelEncoder()
    encoder_disorder = OrdinalEncoder(categories=[['None', 'Sleep Apnea', 'Insomnia']])
    encoder_bmi = OrdinalEncoder(categories=[['Normal', 'Overweight', 'Obese']])
    data['gender'] = label_encoder_gender.fit_transform(data['Gender'])
    
    data['disorder'] = encoder_disorder.fit_transform(data[['Sleep Disorder']])
    data['bmi'] = encoder_bmi.fit_transform(data[['BMI Category']])
    data['gender'] = label_encoder_gender.fit_transform(data['Gender'])
    
    return data

def data_load_sleep(data):
    conn = db_connection()
    cur = conn.cursor()

    # Minden sor beszúrása a táblába
    for i, row in data.iterrows():
        cur.execute("""
            INSERT INTO sleep (gender, age, duration, quality, activity, 
            stress, bmi, heartrate, steps, disorder)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['gender'], row['Age'], row['Sleep Duration'], row['Quality of Sleep'],
              row['Physical Activity Level'], row['Stress Level'], row['bmi'], 
              row['Heart Rate'], row['Daily Steps'], row['disorder']))
        

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
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password
    
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

def save_heart_rate_data(timestamp, heartrate, userProfileId):
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO heartrates (timestamp, heartrate, userProfileId) VALUES (%s, %s, %s)",
                (timestamp, heartrate, userProfileId))
        
        conn.commit()
    except Exception as e:
        print(f"Hiba történt az adat mentésekor: {e}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()
    