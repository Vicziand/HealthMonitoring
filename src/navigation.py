import streamlit as st
from st_pages import Page, Section, add_page_title, hide_pages

home = st.Page("main/home.py", title="Főoldal", icon="🏠")

chd = st.Page("main/chd.py", title="Szívkoszorúér-betegség kockázat", icon="💓")
chd_analizys = st.Page("main/chd_analisys.py", title="Analízis", icon="📊")



sleep = st.Page(
    "main/sleep.py", title="Alvás figyelés", icon="💤"
)

sleep_analizys = st.Page("main/sleep_analisys.py", title="Analízis", icon="📊")

pg = st.navigation(
        {
            "" : [home],
            "Szívkoszorúér-betegség": [chd,chd_analizys],
            "Alvás figyelés": [sleep, sleep_analizys],
        }
)

pg.run()