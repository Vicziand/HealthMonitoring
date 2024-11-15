import streamlit as st


col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.title("Health Monitoring")
with col2:
    st.image("src/health_monitoring.jpg", width=400)
st.write("\n")

st.markdown("""Az alkalmazás célja az egészségügyi adatok folyamatos figyelése és elemzése. A felületen két predikció érhető el:
- Szívkoszorúér-betegség kockázatának előrejelzése
- Alvási rendellenességek felismerésére""")
st.write("\n")

col3, col4 = st.columns(2, gap="small")
with col3:  
    st.markdown("""Az alkalmazás rendelkezik egy bejelentkezés funkcióval, amelyen keresztül a Garminconnect fiókhoz kapcsolódva lehet importálni az aktuális adatokat, amelyek segítségével elvégezhető a predikció.
     A bejelentkezéshez a GarminConnect alkalmazás regisztrációjakor használt felhasználónév és jelszó szükséges""")
with col4:
    st.image("src/smartwatch_photo.jpg", width=400)
st.write("\n")

st.markdown("""Az előrejelzések nem minősülnek valódi orvosi diagnózisnak. Az eredmények kizárólag tájékoztatási célt szolgálnak, és nem helyettesítik az orvosi konzultációt vagy szakértelmet.""")
