import streamlit as st
import plotly.express as px
from data.db_utils import *

def show_heartrate():
    conn = db_connection()
    query_hr = """
        SELECT "timestamp", "heartrate", "userprofileid"
        FROM heartrates;
    """
    data_hr = pd.read_sql(query_hr, conn)
    conn.close()

    # Timestamp átalakítása datetime formátummá
    data_hr['timestamp'] = pd.to_datetime(data_hr['timestamp'], unit='ms')

    # Adatok előkészítése a vizualizációhoz
    data_hr = data_hr.sort_values(by='timestamp')

    # Plotly diagram készítése
    fig = px.line(
        data_hr, 
        x='timestamp', 
        y='heartrate', 
        title='Szívritmus időbeli változása',
        labels={'timestamp': 'Dátum', 'heartrate': 'Szívritmus (bpm)'},
        markers=True
    )

    # Diagram megjelenítése a Streamlitben
    st.plotly_chart(fig)
    
def activities_query():
    conn = db_connection()
    query_hr = """
        SELECT "totalsteps", "averagestresslevel", "sleepingseconds", "activeseconds", "sleepquality", 
            "userprofileid", "calendardate"
        FROM activities;
        """
    data_hr = pd.read_sql(query_hr, conn)
    conn.close()
    return data_hr
    
def show_totalsteps():
    data_hr = activities_query()

    data_hr = data_hr.sort_values(by='calendardate')

    fig = px.line(
        data_hr, 
        x='calendardate', 
        y='totalsteps', 
        title='Napi lépészsám',
        labels={'calendardate': 'Dátum', 'totalsteps': 'Napi lépészsám'},
        markers=True
    )
    fig.update_traces(line=dict(color='yellow'))
    st.plotly_chart(fig)

def show_stress():
    data_hr = activities_query()
    data_hr['averagestresslevel'] = data_hr['averagestresslevel'] / 10
    data_hr = data_hr.sort_values(by='calendardate')

    fig = px.line(
        data_hr, 
        x='calendardate', 
        y='averagestresslevel', 
        title='Stressz-szint',
        labels={'calendardate': 'Dátum', 'averagestresslevel': 'Stressz-szint'},
        markers=True
    )

    fig.update_traces(line=dict(color='red'))
    st.plotly_chart(fig)
    
def show_sleeping_sec():
    data_hr = activities_query()
    data_hr['sleepquality'] = data_hr['sleepquality'] / 10
    data_hr = data_hr.sort_values(by='calendardate')
    
    fig = px.line(
        data_hr, 
        x='calendardate', 
        y='sleepquality', 
        title='Alvás minőség',
        labels={'calendardate': 'Dátum', 'sleepquality': 'Alvás minőség'},
        markers=True
    )

    fig.update_traces(line=dict(color='orange'))

    st.plotly_chart(fig)
    
def show_active_sec():
    data_hr = activities_query()
    data_hr['activeseconds'] = data_hr['activeseconds'] / 60

    data_hr = data_hr.sort_values(by='calendardate')

    fig = px.line(
        data_hr, 
        x='calendardate', 
        y='activeseconds', 
        title='Fizikai aktivitás',
        labels={'calendardate': 'Dátum', 'activeseconds': 'Fizikai aktivitás'},
        markers=True
    )

    fig.update_traces(line=dict(color='green'))

    st.plotly_chart(fig)

def show_sleep_quality():
    data_hr = activities_query()
    data_hr['sleepquality'] = data_hr['sleepquality'] / 10

    data_hr = data_hr.sort_values(by='calendardate')

    fig = px.line(
        data_hr, 
        x='calendardate', 
        y='sleepquality', 
        title='Alvás minőség',
        labels={'calendardate': 'Dátum', 'sleepquality': 'Alvás minőség'},
        markers=True
    )

    fig.update_traces(line=dict(color='magenta'))
    
    st.plotly_chart(fig)

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
    
