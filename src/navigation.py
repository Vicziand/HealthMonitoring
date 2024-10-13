import streamlit as st
from st_pages import Page, Section, add_page_title, hide_pages
from auth.auth import *
from main.garmin import *

home = st.Page("main/home.py", title="Főoldal", icon="🏠")
chd = st.Page("main/chd.py", title="Szívkoszorúér-betegség kockázat", icon="💓")
chd_analizys = st.Page("main/chd_analisys.py", title="Analízis", icon="📊")
sleep = st.Page("main/sleep.py", title="Alvás figyelés", icon="💤")
sleep_analizys = st.Page("main/sleep_analisys.py", title="Analízis", icon="📊")
garmin = st.Page("main/garmin.py", title="Garmin Connect", icon="⌚️")
login_page = st.Page("main/login.py", title="Bejelentkezés", icon="🔑")


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


if st.session_state["authenticated"]:
    # Bejelentkezés után megjelenő menü
    pg = st.navigation(
        {
            "Főoldal": [home],
            "Szívkoszorúér-betegség": [chd, chd_analizys],
            "Alvás figyelés": [sleep, sleep_analizys],
            "Saját adat": [garmin]
        }
    )
    
    show_data()

    if st.sidebar.button("Kijelentkezés"):
        st.session_state["authenticated"] = False
        st.session_state["page"] = "Főoldal"

else:
    # Bejelentkezés előtti menü
    pg = st.navigation(
        {
           "Főoldal": [home],
            "Szívkoszorúér-betegség": [chd, chd_analizys],
            "Alvás figyelés": [sleep, sleep_analizys],
            "Saját adat": [login_page]
        }
    )


# Menü megjelenítése
pg.run()