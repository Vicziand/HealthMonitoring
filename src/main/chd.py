import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from models.supervised_chd import *
from data.db_utils import *

prepare_chd_data()
x,y = create_chd_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = data_preprocessing(x,y)
is_chd = True
models = train_models(X_train_scaled, y_train, is_chd)
st.title("💓 Szívkoszorúér-betegség kockázatának előrejelzése")
st.write("Kérem jelölje a megfelelő adatokat! Amennyiben a megadott intervallumon kívül esik az érték, a legközelebbi szélsőértéket adja meg. ")
         
form = st.form(key="form_settings")
col1, col2, col3 = form.columns([1, 2, 2])

with form:

    age_value = col1.slider(
        "Életkor",
        18,
        80,
        key = "age",
    )

    gender_options = ["férfi","nő"] 
    gender = col1.radio(
        "Neme",
        options = gender_options,
        key = "gender",
        )

    gender_value = 1 if gender == "férfi" else 0

    height_value = col2.slider(
        "Magasság (cm)",
        160,
        200,
        key = "height"
    )

    weight_value = col3.slider(
        "Súly (kg)",
        40,
        250,
        key = "weight",
    )

    bmi_value = weight_value / ((height_value * 0.01) ** 2)

    cigs_per_day_value = col2.slider(
        "Napi elszívott cigaretta mennyisége", 
        min_value=0, max_value=80, value=0, step=1
    )

    heart_rate_value = col3.slider(
        "Nyugalmi pulzus",
        40,
        120,
        key = "heart_rate"
    )

    bp_meds = col2.checkbox(
        "Szed vérnyomáscsökkentő gyógyszert?", 
        value = False,
        key="bpmeds"
    )
    bp_meds_value = 0 if bp_meds == False else 1

    prevalent_stroke = col3.checkbox(
        "Volt korábban stroke-ja?",
        value = False,
        key="prevalent_stroke",
    )
    prevalent_stroke_value = 0 if bp_meds == False else 1

    prevalent_hyp = col2.checkbox(
        "Kezelték már korábban magas vérnyomással?",
        value = False,
        key = "prevalent_hyp",
    )
    prevalent_hyp_value = 0 if prevalent_hyp == False else 1

    diabetes = col3.checkbox(
        "Szenved cukorbetegségben?",
        value = False,
        key = "diabetes"
    )
    diabetes_value = 0 if diabetes == False else 1

    submit_button = st.form_submit_button(label="Elküld")

if submit_button:

    user_data = pd.DataFrame({
        'male' : [gender_value],
        'age': [age_value],
        'cigsperday' : [cigs_per_day_value],
        'bpmeds' : [bp_meds_value],
        'prevalentstroke' : [prevalent_stroke_value],
        'prevalenthyp': [prevalent_hyp_value],
        'diabetes': [diabetes_value],
        'heartrate': [heart_rate_value],
        'bmi': [bmi_value]
    })

    user_data_scaled = scaler.transform(user_data)
    user_pred = models['Random Forest'].predict(user_data_scaled)
    user_prob = models['Random Forest'].predict_proba(user_data_scaled)
    chd_prob = user_prob[0][1]

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = chd_prob * 100,
        title = {'text': "Koronária szívbetegség valószínűsége 10 éven belül (%)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps' : [
                {'range': [0, 25], 'color': "green"},
                {'range': [25, 50], 'color': "yellowgreen"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 100], 'color': "red"}],
        }
    ))

    st.plotly_chart(fig)
    
 # Kockázati szint meghatározása
    if chd_prob * 100 > 50:
        risk_level = "magas"
    elif chd_prob * 100 > 25:
        risk_level = "mérsékelt"
    else:
        risk_level = "alacsony"

    messages = [
        f"A megadott paraméterek alapján {risk_level} a kockázati szint.",
        "Az életkor előrehaladtával növekszik a kockázat."
    ]

    if cigs_per_day_value > 0:
        messages.append("A dohányzás jelentősen növeli a szív és érrendszeri problémák kockázatát.")
    if bmi_value > 30:
        messages.append("Az ön testömegindexe alapján túlsúlyos kategóriába tartozik. Az egészséges életmód és a fittség hozzájárul a kockázat csökkentéséhez.")

    st.markdown("""
    <div style="text-align: center;">
        <ul style="list-style-position: inside;">
    """, unsafe_allow_html=True)

    for message in messages:
        st.markdown(f"<li>{message}</li>", unsafe_allow_html=True)

    st.markdown("</ul></div>", unsafe_allow_html=True)