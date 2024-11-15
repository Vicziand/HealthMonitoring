import pandas as pd
import streamlit as st
from data import db_utils
from models.supervised_chd import *

def create_sleep_variables():
    
    conn = db_utils.db_connection()
    query = """
    SELECT "gender", "age", "duration", "quality", "activity", "stress", 
       "bmi", "heartrate", "steps", "disorder"
    FROM sleep;
    """ 
    data = db_utils.fetch_data(query)
    conn.close()
    
    # Független változók
    x = data[['gender', 'age', 'duration', 'quality', 'activity', 
              'stress', 'bmi', 'heartrate', 'steps']]
    
    # Függő változó
    y = data[['disorder']]
    return x,y
 
def sleep_data_preprocessing(x,y):
    x_train, x_test, y_train, y_test = split_data(x, y)
    X_train_scaled, X_test_scaled, scaler = data_scaler(x_train, x_test)
    return X_train_scaled, X_test_scaled, scaler, y_train, y_test
 
 