import streamlit as st
from st_pages import Page, Section, add_page_title, hide_pages
#st.set_page_config(layout="wide")
from auth.auth import *
from main.garmin import *
import psutil

def monitor_resources():
    # Aktuális folyamat (Streamlit alkalmazás) lekérése
    process = psutil.Process(os.getpid())

    # CPU használat lekérése
    cpu_usage = process.cpu_percent(interval=1)

    # RAM használat lekérése
    memory_info = process.memory_info()
    ram_usage = memory_info.rss / (1024 * 1024)  # RAM használat MB-ban

    #st.write(f"Az alkalmazás CPU kihasználása: {cpu_usage}%")
    #st.write(f"Az alkalmazás memóriahasználata: {ram_usage:.2f} MB")


home = st.Page("main/home.py", title="Főoldal", icon="🏠")
chd = st.Page("main/chd.py", title="Szívkoszorúér-betegség kockázat", icon="💓")
chd_analizys = st.Page("main/chd_analisys.py", title="Analízis", icon="📊")
sleep = st.Page("main/sleep.py", title="Alvás figyelés", icon="💤")
sleep_analizys = st.Page("main/sleep_analisys.py", title="Analízis", icon="📊")
garmin_connect = st.Page("main/garmin_connect.py", title="Garmin Connect", icon="⌚️")
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
            "Saját adat": [garmin_connect]
        }
    )

    if st.sidebar.button("Kijelentkezés"):
        st.session_state["authenticated"] = False
        st.session_state["page"] = "Főoldal"
    monitor_resources()
    show_data()

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
    monitor_resources()

# Menü megjelenítése
pg.run()


