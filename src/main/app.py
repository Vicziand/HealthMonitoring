import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics import classification_report
import statsmodels.api as sm
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt


Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")

data = Rawdata[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']].dropna()
st.write(data[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI','TenYearCHD']])

std_corr = data.corr()
print(std_corr['TenYearCHD'].sort_values(ascending = False))


# független változók
x = data[['male','age','currentSmoker','cigsPerDay','BPMeds','prevalentStroke','prevalentHyp','diabetes','heartRate','BMI']].dropna()
# függő változók
y = data[['TenYearCHD']]

smote = SMOTE(random_state=42)
X_ros, y_ros = smote.fit_resample(x, y)
ros_chd_plot=y_ros.value_counts().plot(kind='bar')
ros_chd_plot = y_ros.value_counts().plot(kind='bar')

st.write("Kiegyensúlyozott adatkészlet osztályeloszlása:")
st.pyplot(plt.gcf())

# Adatok felosztása tanuló és teszt adatokra (80% tanuló, 20% teszt, randomizációs mag 42 - általánosan használt érték)
x_train, x_test, y_train, y_test = train_test_split(X_ros, y_ros, test_size = 0.2, random_state = 42)

# Adatok skálázása
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(x_train)
X_test_scaled = scaler.transform(x_test)


LogRegModel = LogisticRegression(max_iter = 1000, class_weight='balanced')

LogRegModel.fit(X_train_scaled, y_train.values.ravel())

y_pred = LogRegModel.predict(X_test_scaled)

st.write(y_pred)

accuracy = accuracy_score(y_test, y_pred)
st.write(f"A modell pontossága: {accuracy * 100:.2f}%")

cm = confusion_matrix(y_test, y_pred)
st.write(f"Zavarási mátrix:\n{cm}")
print(classification_report(y_test, y_pred))

your_data = pd.DataFrame({
    'male' : [0],
    'age': [50],
    'currentSmoker': [0],
    'cigsPerDay' : [0],
    'BPMeds' : [0],
    'prevalentStroke' : [0],
    'prevalentHyp': [0],
    'diabetes': [0],
    'heartRate': [60],
    'BMI': [24.9]
})

your_data_scaled = scaler.transform(your_data)
your_pred = LogRegModel.predict(your_data_scaled)
your_prob = LogRegModel.predict_proba(your_data_scaled)
chd_prob = your_prob[0][1]

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = chd_prob * 100,
    title = {'text': "Koronária szívbetegség valószínűsége (%)"},
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
    'Feature': ['male', 'age', 'currentSmoker', 'cigsPerDay', 'BPMeds', 
                'prevalentStroke', 'prevalentHyp', 'diabetes', 'heartRate', 'BMI'],
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