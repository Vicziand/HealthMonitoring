import streamlit as st
from data.db_utils import *


def show_data():
    
    conn = db_connection()
    query_act = """
        SELECT "totalsteps", "averagestresslevel", "sleepingseconds", "activeseconds", "sleepquality", 
            "userprofileid", "calendardate"
        FROM activities;
        """
    query_hr = """
        SELECT "timestamp", "heartrate", "userprofileid"
        FROM heartrates;
        """ 


    data_act = pd.read_sql(query_act, conn)
    data_hr = pd.read_sql(query_hr, conn)
    conn.close()
    
    
    heart_rate_median = data_hr['heartrate'].median()
    total_steps_median = data_act['totalsteps'].median()
    average_stress_median = data_act['averagestresslevel'].median() / 10
    sleeping_seconds_median = data_act['sleepingseconds'].median() /3600
    active_second_median = data_act['activeseconds'].median() / 60
    sleep_quality_median = data_act['sleepquality'].median() /10
    
    st.sidebar.metric(label="Pulzus", value = round(heart_rate_median))
    st.sidebar.metric(label="Napi lépésszám", value=int(round(total_steps_median, -2)))
    st.sidebar.metric(label="Stressz-szint", value=round(average_stress_median))
    st.sidebar.metric(label="Alvás hossza (h)", value=round(sleeping_seconds_median, 1))
    st.sidebar.metric(label="Fizikai aktivitás", value = round(active_second_median))
    st.sidebar.metric(label="Alvás minősége", value = round(sleep_quality_median))