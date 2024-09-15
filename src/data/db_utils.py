import psycopg2
from sqlalchemy import create_engine
#SQLAlchemy egy python csomag, ami sql adatbázis kapcsolat létrehozására szolgál
import pandas as pd
#A Pandas egy Python könyvtár, ami adatok feldolgozására és elemzésére szolgál.

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
    cur.execute('''
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
    ''')
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

    data = Rawdata[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']].dropna().rename(columns=str.lower)
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
    