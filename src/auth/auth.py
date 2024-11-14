import streamlit as st
from garminconnect import Garmin
import bcrypt

import os
import sys
# A könyvtár relatív elérési útja
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data.garmin_data_loader import *

def authenticate_garmin(email, password):
    try:
        # Ellenőrizzük, hogy a felhasználó létezik-e az adatbázisban
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None:
            return False

        # A jelszót bytes formátumba konvertáljuk az ellenőrzéshez
        stored_hashed_password = row[0].encode('utf-8')

        # Ellenőrizzük a jelszót a bcrypt használatával
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            st.session_state["authenticated"] = True
            return True
        else:
            st.session_state["authenticated"] = False
            return False

    except psycopg2.Error as e:
        st.error(f"Adatbázis hiba: {e}")
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
