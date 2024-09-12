import pandas as pd
import streamlit as st
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import xgboost as xgb
from data import db_utils

def create_table():
    conn = db_utils.db_connection()
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
    
def clear_table():
    conn = db_utils.db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chd;")
    conn.commit()
    cur.close()
    conn.close()

def data_load():
    Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")

    data = Rawdata[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']].dropna().rename(columns=str.lower)
    #st.write(data[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']])
    conn = db_utils.db_connection()
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

def create_variables():
    
    conn = db_utils.db_connection()
    query = """
    SELECT "male", "age", "currentsmoker", "cigsperday", "bpmeds", "prevalentstroke", 
       "prevalenthyp", "diabetes", "heartrate", "bmi", "tenyearchd"
    FROM chd;
    """ 

    data = pd.read_sql(query, conn)
    conn.close()
    print(data.columns)
    
    # Független változók
    x = data[['male', 'age', 'currentsmoker', 'cigsperday', 'bpmeds', 
              'prevalentstroke', 'prevalenthyp', 'diabetes', 'heartrate', 'bmi']]
    
    # Függő változó
    y = data[['tenyearchd']]
    return x,y

def smote(x,y):
    smote = SMOTE(random_state=42)
    X_ros, y_ros = smote.fit_resample(x, y)
    y_ros.value_counts().plot(kind='bar')
    y_ros.value_counts().plot(kind='bar')
    return X_ros, y_ros

#st.write("Kiegyensúlyozott adatkészlet osztályeloszlása:")
#st.pyplot(plt.gcf())

def split_data(X_ros, y_ros):
    # Adatok felosztása tanuló és teszt adatokra (80% tanuló, 20% teszt, randomizációs mag 42 - általánosan használt érték)
    x_train, x_test, y_train, y_test = train_test_split(X_ros, y_ros, test_size = 0.2, random_state = 42)
    return x_train, x_test, y_train, y_test

def data_scaler(x_train, x_test):
    # Adatok skálázása
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(x_train)
    X_test_scaled = scaler.transform(x_test)
    return X_train_scaled, X_test_scaled, scaler

def train_log_reg(X_train_scaled, y_train):
    LogRegModel = LogisticRegression(max_iter = 1000, class_weight='balanced')

    LogRegModel.fit(X_train_scaled, y_train.values.ravel())
    return LogRegModel

def train_random_forest(X_train_scaled, y_train):
    RFModel = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    RFModel.fit(X_train_scaled, y_train)
    return RFModel

def train_xgboost(X_train_scaled, y_train):
    XGBModel = xgb.XGBClassifier()
    XGBModel.fit(X_train_scaled, y_train)
    return XGBModel

def model_accuracy(model, X_test_scaled, y_test):
    y_pred = model.predict(X_test_scaled)

    #st.write(y_pred)
    # Zavarási mátrix és részletes elemzés
    cm = confusion_matrix(y_test, y_pred)
    print(f"Zavarási mátrix:\n{cm}")
    print(classification_report(y_test, y_pred))

    accuracy = accuracy_score(y_test, y_pred)
    st.write(f"A modell pontossága: {accuracy * 100:.2f}%")