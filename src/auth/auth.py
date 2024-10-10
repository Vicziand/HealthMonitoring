import streamlit as st
from garminconnect import Garmin
import bcrypt

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from data.garmin_data_loader import *

def authenticate_garmin(email, password):
    # Próbálja meg a Garmin Connect API-val bejelentkezni
    if garmin_login(email, password):
        st.session_state["authenticated"] = True
        return True
    else:
        st.session_state["authenticated"] = False
        return False
    
    
def login():
    st.title("Bejelentkezés Garmin Connect segítségével")

    email = st.text_input("Email")
    password = st.text_input("Jelszó", type="password")

    if st.button("Bejelentkezés"):
        if authenticate_garmin(email, password):
            st.success("Sikeres bejelentkezés a Garmin Connect-en keresztül!")
            
        else:
            st.error("Hiba történt a bejelentkezéskor. Ellenőrizd az e-mail címet és a jelszót.")

    if st.session_state.get("authenticated"):
        st.write("Üdvözlünk a felületen!")
    else:
        st.write("Kérjük jelentkezz be a Garmin Connect adataiddal.")

if __name__ == "__main__":
    login()
