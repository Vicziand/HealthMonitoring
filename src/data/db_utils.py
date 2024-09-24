import psycopg2
from sqlalchemy import create_engine
#SQLAlchemy egy python csomag, ami sql adatbázis kapcsolat létrehozására szolgál
import pandas as pd
#A Pandas egy Python könyvtár, ami adatok feldolgozására és elemzésére szolgál.
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import LabelEncoder

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

def create_chd_table():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chd (
            id SERIAL PRIMARY KEY,
            male INTEGER,
            age INTEGER,
            currentsmoker INTEGER,
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

def data_load_chd():
    Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")

    data = Rawdata[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']].dropna()
    #st.write(data[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']])
    conn = db_connection()
    cur = conn.cursor()

    # Minden sor beszúrása a táblába
    for i, row in data.iterrows():
        cur.execute("""
            INSERT INTO chd (male, age, currentsmoker, cigsperday, bpmeds, 
            prevalentstroke, prevalenthyp, diabetes, heartrate, bmi, tenyearchd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))

    conn.commit()
    cur.close()
    conn.close()
    
def prepare_chd_data():
    create_chd_table()
    clear_chd_table()
    data_load_chd()
    
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