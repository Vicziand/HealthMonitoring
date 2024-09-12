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

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from models.supervised import *

create_table()
clear_table()
data_load()
x, y = create_variables()

X_ros, y_ros = smote(x,y)

x_train, x_test, y_train, y_test = split_data(X_ros, y_ros)

X_train_scaled, X_test_scaled, scaler = data_scaler(x_train,x_test)

LogRegModel = train_log_reg(X_train_scaled, y_train)
RFModel = train_random_forest(X_train_scaled, y_train)
XGBModel = train_xgboost(X_train_scaled, y_train)

model_accuracy(XGBModel,X_test_scaled,y_test)

# Zavarási mátrix és részletes elemzés
#cm = confusion_matrix(y_test, y_pred)
#st.write(f"Zavarási mátrix:\n{cm}")
#st.write(classification_report(y_test, y_pred))

your_data = pd.DataFrame({
    'male' : [1],
    'age': [70],
    'currentsmoker': [0],
    'cigsperday' : [0],
    'bpmeds' : [0],
    'prevalentstroke' : [0],
    'prevalenthyp': [0],
    'diabetes': [0],
    'heartrate': [70],
    'bmi': [40]
})

your_data_scaled = scaler.transform(your_data)
your_pred = XGBModel.predict(your_data_scaled)
your_prob = XGBModel.predict_proba(your_data_scaled)
chd_prob = your_prob[0][1]

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = chd_prob * 100,
    title = {'text': "Koronária szívbetegség valószínűsége 10 éven belül (%)"},
    gauge = {
        'axis': {'range': [0, 100]},
        'bar': {'color': "black"},
        'steps' : [
            {'range': [0, 25], 'color': "lightgreen"},
            {'range': [25, 50], 'color': "green"},
            {'range': [50, 75], 'color': "orange"},
            {'range': [75, 100], 'color': "red"}],
    }
))

# Modell koefficiensek lekérése
coef = LogRegModel.coef_[0]

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

menu = st.sidebar.selectbox('Válassz egy elemzést:', ['Modell 1', 'Modell 2', 'Modell 3'])
menu2 = st.sidebar.selectbox('Válassz egy elemzést:', ['Modell 4', 'Modell 5', 'Modell 6'])

# Modell 1
if menu == 'Modell 1':
    st.write("Ez a Modell 1 elemzés.")
    # Modell 1 kódja

# Modell 2
elif menu == 'Modell 2':
    st.write("Ez a Modell 2 elemzés.")
    # Modell 2 kódja

# Modell 3
elif menu == 'Modell 3':
    st.write("Ez a Modell 3 elemzés.")
    # Modell 3 kódja