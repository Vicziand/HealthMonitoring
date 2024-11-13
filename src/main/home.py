import streamlit as st

st.title("Health Monitoring")
st.image("src/health_monitoring.jpg", width=400)

st.markdown("""Az alkalmazás célja az egészségügyi adatok folyamatos figyelése és elemzése. A felületen két predikció érhető el: szívkoszorúér-betegség kockázatának előrejelzésére, valamint az alvási rendellenességek felismerésére.

Az alkalmazás rendelkezik egy bejelentkezés funkcióval, amelyen keresztül a Garminconnect fiókhoz kapcsolódva lehet importálni az aktuális adatokat, amelyek segítségével elvégezhető a predikció.
Bejelentkezés után egy extra funkció is elérhetővé válik, amely a frissen betöltött adatok grafikus megjelenítését biztosítja, hogy könnyedén nyomon követhesd a eredményidet. A bejelentkezés hez a GarminConnect alkalmazás regisztrációjakor használt felhasználónév és jelszó szükséges

Az előrejelzések nem minősülnek valódi orvosi diagnózisnak. Az eredmények kizárólag tájékoztatási célt szolgálnak, és nem helyettesítik az orvosi konzultációt vagy szakértelmet.""")


