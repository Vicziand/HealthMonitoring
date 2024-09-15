import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import statsmodels.api as sm
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import tensorflow as tf


import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from models.supervised_chd import *
from data.db_utils import *

prepare_chd_data()
x,y = create_chd_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = data_preprocessing(x,y)

models = train_models(X_train_scaled, y_train)

for model in models:
   model_accuracy(model, X_test_scaled, y_test)
   
# Zavarási mátrix és részletes elemzés
#cm = confusion_matrix(y_test, y_pred)
#st.write(f"Zavarási mátrix:\n{cm}")
#st.write(classification_report(y_test, y_pred))

form = st.form(key="form_settings")
col1, col2, col3 = form.columns([1, 2, 2])

age_value = col1.slider(
    "Életkor",
    16,
    100,
    key = "age",
)

gender_options = ["férfi","nő"] 
gender = col1.radio(
    "Neme",
    options = gender_options,
    key = "gender",
    )

gender_value = 1 if gender == "férfi" else 0
st.write(f"Választott nem: {gender}, numerikus érték: {gender_value}")

height_value = col2.slider(
    "Magasság (cm)",
    130,
    220,
    key = "height"
)

weight_value = col3.slider(
    "Súly (kg)",
    20,
    250,
    key = "weight",
)

bmi_value = weight_value / ((height_value * 0.01) ** 2)

cigs_per_day_value = col2.slider(
    "Napi elszívott cigaretta mennyisége", 
    min_value=0, max_value=80, value=0, step=1
)

current_smoker_value = 0 if cigs_per_day_value == 0 else 1

heart_rate_value = col3.slider(
    "Nyugalmi pulzus",
    40,
    100,
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

st.write(f"Bmi {bmi_value}")
st.write(f"Dohányzik? {current_smoker_value}")
st.write(f"Mennyit Dohányzik? {cigs_per_day_value}")
st.write(f"Életkor: {age_value}")
st.write(f"Pulzus {heart_rate_value}")
st.write(f"Bpm {bp_meds_value}")
st.write(f"Stroke {prevalent_stroke_value}")
st.write(f"Magas vérnyomás {prevalent_hyp_value}")
st.write(f"Cukorbetegség {diabetes_value}")

form.form_submit_button(label="Elfogad")

your_data = pd.DataFrame({
    'male' : [gender_value],
    'age': [age_value],
    'currentsmoker': [current_smoker_value],
    'cigsperday' : [cigs_per_day_value],
    'bpmeds' : [bp_meds_value],
    'prevalentstroke' : [prevalent_stroke_value],
    'prevalenthyp': [prevalent_hyp_value],
    'diabetes': [diabetes_value],
    'heartrate': [heart_rate_value],
    'bmi': [bmi_value]
})

your_data_scaled = scaler.transform(your_data)
your_pred = models[1].predict(your_data_scaled)
your_prob = models[1].predict_proba(your_data_scaled)
chd_prob = your_prob[0][1]

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

# Modell koefficiensek lekérése
coef = models[0].coef_[0]

# Változók neveinek hozzárendelése a koefficiensekhez
feature_importance = pd.DataFrame({
    'Feature': ['male', 'age', 'currentsmoker', 'cigsperday', 'bpmeds', 
                'prevalentstroke', 'prevalenthyp', 'diabetes', 'heartrate', 'bmi'],
    'Coefficient': coef
})

# Koefficiensek abszolút értékének vizsgálata (hogy jobban lássuk a súlyozást)
feature_importance['Abs_Coefficient'] = np.abs(feature_importance['Coefficient'])
feature_importance = feature_importance.sort_values(by='Abs_Coefficient', ascending=False)

# Eredmények megjelenítése
print(feature_importance)

st.plotly_chart(fig)

print(f"Saját predikált koronária szívbetegség valószínűsége (CHD): {your_prob[0][1]:.2f}")
print(f"Saját predikált koronária kockázat (TenYearCHD): {your_pred[0]}")

