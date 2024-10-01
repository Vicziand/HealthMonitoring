import pandas as pd
import streamlit as st
import sweetviz as sv
import ydata_profiling as pp
import matplotlib.pyplot as plt
import seaborn as sns

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from models.supervised_chd import *
from data.db_utils import *


Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")
profile = pp.ProfileReport(Rawdata)
profile.to_file("output.html")

with open("output.html", "r", encoding='utf-8') as f:
    html_content = f.read()

# HTML tartalom megjelenítése
st.components.v1.html(html_content, height=600, scrolling=True)


missing_columns = Rawdata.select_dtypes(include='number').columns[Rawdata.isnull().any()]
missing_data = Rawdata[missing_columns]

st.write(missing_data.dtypes)
st.write(missing_data.nunique())

sns.set(rc={'figure.figsize':(15,5)})
ax=sns.boxplot(data=missing_data)
ax.set_xticklabels(ax.get_xticklabels(),rotation=45)
st.pyplot(plt)

data = data_clean_chd()
correlation_chd(data)

fig, ax = plt.subplots(figsize=(10, 6))
sns.set()
chd_plot = data['TenYearCHD'].value_counts().plot(kind='bar', color=['#70C454', '#E74C3C'], ax=ax)
ax.set_xlabel('TenYearCHD (0: Nem volt kardiovaszkuláris probléma, 1: Volt kardivaszkuláris probléma)', fontsize=12, labelpad=10)
ax.set_ylabel('Darab', fontsize=12, labelpad=10)
ax.set_xticks([0, 1])
ax.set_xticklabels(['0', '1'], fontsize=11)
st.pyplot(fig)