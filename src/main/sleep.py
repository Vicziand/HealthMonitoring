import streamlit as st
import os
import sys
# A könyvtár relatív elérési útja
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from models.supervised_chd import *
from models.supervised_sleep import *
from data.db_utils import *

data = data_clean_sleep()
prepare_sleep_data()
x,y = create_sleep_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = sleep_data_preprocessing(x,y)

SVMModel = train_SVM(X_train_scaled, y_train)
KNN = train_KNN(X_train_scaled, y_train)
XGBoost = train_xgboost(X_train_scaled, y_train, is_chd=False)

model_accuracy(XGBoost, X_test_scaled, y_test)
st.title("💤 Alvási rendellenesség felismerés")
st.write("Kérem jelölje a megfelelő adatokat! Amennyiben a megadott intervallumon kívül esik az érték, a legközelebbi szélsőértéket adja meg.")
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
    
    stress_value = col3.slider(
        "Stressz-szint",
        0,
        10,
        key = "stress",
    )
    
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

    heart_rate_value = col2.slider(
        "Nyugalmi pulzus",
        40,
        100,
        key = "heart_rate"
    )
    
    steps_value = col3.slider(
        "Napi lépésszám",
        1000,
        10000,
        step = 100,
        key = "steps"
    )
    
    submit_button = st.form_submit_button(label="Elküld")
    
if submit_button:

    user_data = pd.DataFrame({
    'gender' : [gender_value],
    'age': [age_value],
    'duration': [duration_value],
    'quality' : [quality_value],
    'activity' : [activity_value],
    'stress' : [stress_value],
    'bmi': [bmi_value],
    'heartrate': [heart_rate_value],
    'steps': [steps_value],
    })
    
    user_data_scaled = scaler.transform(user_data)
    user_pred = XGBoost.predict(user_data_scaled)

    if user_pred == 0:
        st.success("Nincs rendellenesség")
        st.markdown("""
                    - Rendszeres testmozgás növeli az alvás minőséget.
                    - Ügyeljen a változatos étrendre.
                    - Éjszaka gondoskodjon a megfelelő fényviszonyokról.
                """)
    elif user_pred == 1:
        st.warning("Alvási apnoé")
        st.markdown("""
                    - Érdemes lehet orvosi segítséget igényelni.
                    - Fontos a rendszeres testmozgás.
                    - Az oldalt fekvő alvási pozíció gyakran segíthet az apnoés tünetek csökkentésében.
                    - Az alkohol és egyes nyugtatók fokozhatják az izmok ellazulását, ami növelheti az apnoés tüneteket.
                    - A dohányzás gyulladást okozhat a légutakban, ami súlyosbíthatja az apnoés tüneteket.
                    - A száraz levegő irritálhatja a légutakat. A párásító készülék használata segíthet enyhíteni a torok szárazságát és az orrdugulást, ami javíthatja a légzést alvás közben.
                """)
    else:
        st.warning("Insomnia")
        st.markdown("""
                    - Érdemes lehet orvosi segítséget igényelni.
                    - Kerülje az elektronikai eszközök használatát lefekvés előtt.
                    - Fontos a rendszeres testmozgás.
                    - A napközbeni rövid alvásokat kerülje.
                    - Koffeint és a nehéz ételeket kerülje lefekvés előtt.
                    - Hozzon létre alvásbarát környezetet.
                    - Fontos a stresszkezelés.
                """)
    
    print(user_pred)