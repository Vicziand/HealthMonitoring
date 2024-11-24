import streamlit as st
from garminconnect import Garmin

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data.garmin_data_loader import *

def authenticate_garmin(email, password):
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
            st.error("Hiba történt a bejelentkezéskor. Ellenőrizze az e-mail címet és a jelszót.")

if __name__ == "__main__":
    login()
