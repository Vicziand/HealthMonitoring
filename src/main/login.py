import streamlit as st
import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from auth.auth import *

st.title("Bejelentkezés oldal")
login()