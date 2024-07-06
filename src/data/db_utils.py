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
