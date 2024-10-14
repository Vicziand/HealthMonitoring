import pandas as pd
import streamlit as st
import sweetviz as sv
import ydata_profiling as pp
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, accuracy_score

import sys
# Hozzáadjuk a könyvtárat az elérési úthoz
sys.path.append('I:/NJE-GAMF/Szakdolgozat/HealthMonitoring/src')
from models.supervised_chd import *
from data.db_utils import *


Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")



missing_columns = Rawdata.select_dtypes(include='number').columns[Rawdata.isnull().any()]
missing_data = Rawdata[missing_columns]


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

prepare_chd_data()
x,y = create_chd_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = data_preprocessing(x,y)

models = train_models(X_train_scaled, y_train)

roc_data = {}
accuracy_data = {}

for model_name, model in models.items():
    if hasattr(model, "predict_proba"):
        y_scores = model.predict_proba(X_test_scaled)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_scores)
        auc_value = auc(fpr, tpr)
        roc_data[model_name] = (fpr, tpr, auc_value)
    
    
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    accuracy_data[model_name] = accuracy

# Accuracy ábrázolás oszlopdiagram
plt.figure(figsize=(10, 6))
plt.bar(accuracy_data.keys(), accuracy_data.values(), color=['blue', 'orange', 'green', 'red', 'purple'])
plt.xlabel('Modellek')
plt.ylabel('Pontosság (Accuracy)')
plt.title('Modellek pontosságának összehasonlítása')
plt.ylim([0, 1])
plt.xticks(rotation=45)

st.pyplot(plt)

# ROC ábrázolás
plt.figure()
for model_name, (fpr, tpr, auc_value) in roc_data.items():
    plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc_value:.2f})')


plt.plot([0, 1], [0, 1], color='gray', linestyle='--') 
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('ROC Curve Comparison for Multiple Models')
plt.legend(loc="lower right")


st.pyplot(plt)

