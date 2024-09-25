import streamlit as st

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from models.supervised_chd import *
from models.supervised_sleep import *
from data.db_utils import *


data = data_clean_sleep()
prepare_sleep_data()
x,y = create_sleep_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = sleep_data_preprocessing(x,y)

LogRegModel = train_log_reg(X_train_scaled, y_train)
model_accuracy(LogRegModel, X_test_scaled, y_test)

st.write(data)

your_data = pd.DataFrame({
    'gender' : [1],
    'age': [27],
    'duration': [8],
    'quality' : [8],
    'activity' : [45],
    'stress' : [4],
    'bmi': [1],
    'heartrate': [70],
    'steps': [5200],
})

form = st.form(key="form_settings")
col1, col2, col3 = form.columns([1, 2, 2])

with form:

    gender_options = ["férfi","nő"] 
    gender = col1.radio(
        "Neme",
        options = gender_options,
        key = "gender",
        )

    gender_value = 1 if gender == "férfi" else 0
    
    age_value = col1.slider(
        "Életkor",
        16,
        90,
        key = "age",
    )
    
    duration_value = col2.slider(
        "Alvás hossza (h)",
        5.0,
        10.0,
        step = 0.1,
        format="%.1f",
        key = "duration",
    )
    
    quality_value = col3.slider(
        "Alvás minősége",
        0,
        10,
        key = "quality",
    )
    
    activity_value = col2.slider(
        "Fizikai aktivitás",
        20,
        100,
        key = "activity",
    )
    
    quality_value = col3.slider(
        "Stressz-szint",
        0,
        10,
        key = "stress",
    )
    
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

    heart_rate_value = col2.slider(
        "Nyugalmi pulzus",
        40,
        100,
        key = "heart_rate"
    )
    
    heart_rate_value = col3.slider(
        "Napi lépésszám",
        1000,
        10000,
        step = 100,
        key = "steps"
    )
    

    submit_button = st.form_submit_button(label="Elküld")

your_data_scaled = scaler.transform(your_data)
your_pred = LogRegModel.predict(your_data_scaled)

st.write(your_pred)