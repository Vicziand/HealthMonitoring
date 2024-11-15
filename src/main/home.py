import streamlit as st

st.markdown("<h1 style='text-align: center;'>Health Monitoring</h1>", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="small")
with col1:
    st.markdown("""
        <div style="
            background-color: #2f2f2f; 
            border-radius: 15px; 
            padding: 20px; 
            color: white;
        ">
            <p>Az alkalmazás célja az egészségügyi adatok folyamatos figyelése és elemzése. A felületen két predikció érhető el:</p>
            <ul>
                <li>Szívkoszorúér-betegség kockázatának előrejelzése</li>
                <li>Alvási rendellenességek felismerésére</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.image("src/health_monitoring.jpg", width=350)

st.write("\n")

col3, col4 = st.columns(2, gap="small",  vertical_alignment="center")
with col3:
    st.markdown("""
        <div style="
            background-color: #2f2f2f; 
            border-radius: 15px; 
            padding: 20px; 
            color: white;
        ">
            <p>Az alkalmazás rendelkezik egy bejelentkezés funkcióval, amelyen keresztül a Garminconnect fiókhoz kapcsolódva lehet importálni az aktuális adatokat, amelyek segítségével elvégezhető a predikció.</p>
            <p>A bejelentkezéshez a GarminConnect alkalmazás regisztrációjakor használt felhasználónév és jelszó szükséges.</p>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.image("src/smartwatch_photo.jpg", width=350)
st.write("\n")

st.markdown("""Az előrejelzések nem minősülnek valódi orvosi diagnózisnak. Az eredmények kizárólag tájékoztatási célt szolgálnak, és nem helyettesítik az orvosi konzultációt vagy szakértelmet.""")


