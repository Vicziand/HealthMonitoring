import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_score, recall_score, f1_score
import numpy as np

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.supervised_chd import *
from data.db_utils import *

Rawdata = pd.read_csv("src/data/raw/training_data_chd.csv")

missing_columns = Rawdata.select_dtypes(include='number').columns[Rawdata.isnull().any()]
missing_data = Rawdata[missing_columns]

col = st.columns((3, 3, 3), gap='medium')


st.markdown('#### Tanító adatbázis')
data = data_clean_chd()
st.write(data)

with col[0]:
    sns.set(rc={'figure.figsize':(11,6)})
    ax=sns.boxplot(data=missing_data)
    ax.set_xticklabels(ax.get_xticklabels(),rotation=45)
    st.markdown('#### Kiugró értékek')
    st.pyplot(plt)

with col[1]:
    st.markdown('#### Korrelációs mátrix')
    correlation_chd(data)

with col[2]:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set()
    chd_plot = data['TenYearCHD'].value_counts().plot(kind='bar', color=['#70C454', '#E74C3C'], ax=ax)
    ax.set_xlabel('TenYearCHD (0: Nem volt kardiovaszkuláris probléma, 1: Volt kardivaszkuláris probléma)', fontsize=12, labelpad=10)
    ax.set_ylabel('Darab', fontsize=12, labelpad=10)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['0', '1'], fontsize=11)
    st.markdown('#### Eloszlás vizsgálat')
    st.pyplot(fig)

prepare_chd_data()
x,y = create_chd_variables()
X_train_scaled, X_test_scaled, scaler, y_train, y_test = data_preprocessing(x,y)
is_chd = True
models = train_models(X_train_scaled, y_train, is_chd)

roc_data = {}
accuracy_data = {}
precision_data = {}
recall_data = {}
f1_data = {}

for model_name, model in models.items():
    if hasattr(model, "predict_proba"):
        y_scores = model.predict_proba(X_test_scaled)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_scores)
        auc_value = auc(fpr, tpr)
        roc_data[model_name] = (fpr, tpr, auc_value)
    
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    accuracy_data[model_name] = accuracy
    precision_data[model_name] = precision
    recall_data[model_name] = recall
    f1_data[model_name] = f1

# Accuracy ábrázolás oszlopdiagram
with col[0]:
    st.markdown('#### Accuracy')
    plt.figure(figsize=(10, 6))
    bars = plt.bar(accuracy_data.keys(), accuracy_data.values(), color=['blue', 'orange', 'green', 'red', 'purple'])
    plt.xlabel('Modellek')
    plt.ylabel('Pontosság (Accuracy)')
    plt.title('Modellek pontosságának összehasonlítása')
    plt.ylim([0, 1])
    plt.xticks(rotation=45)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f'{yval:.2%}', ha='center', va='bottom')

    st.pyplot(plt)

# Precision, Recall és F1-score ábrázolása
with col[1]:
    metrics = ['Precision', 'Recall', 'F1-score']
    x = np.arange(len(models))
    width = 0.2

    st.markdown('#### Precision,Recall, F1-score')
    plt.figure(figsize=(12, 6))
    precision_values = [precision_data.get(m, 0) for m in models.keys()]
    recall_values = [recall_data.get(m, 0) for m in models.keys()]
    f1_values = [f1_data.get(m, 0) for m in models.keys()]

    bars1 = plt.bar(x - width, precision_values, width, label='Precision', color='blue')
    bars2 = plt.bar(x, recall_values, width, label='Recall', color='orange')
    bars3 = plt.bar(x + width, f1_values, width, label='F1-score', color='green')

    plt.xlabel('Modellek')
    plt.ylabel('Értékek')
    plt.title('Precision, Recall és F1-score összehasonlítása modellekenként')
    plt.xticks(x, models.keys(), rotation=45)
    plt.ylim([0, 1])

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)

    for bar in bars1:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')

    for bar in bars2:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')

    for bar in bars3:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')

    st.pyplot(plt)


# ROC ábrázolás
with col[2]:
    st.markdown('#### ROC-görbe')
    plt.figure()
    for model_name, (fpr, tpr, auc_value) in roc_data.items():
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc_value:.2f})')


    plt.plot([0, 1], [0, 1], color='gray', linestyle='--') 
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Hamis pozitív arány')
    plt.ylabel('Valódi pozitív arány')
    plt.title('ROC görbe összehasonlítása a modelleken')
    plt.legend(loc="lower right")

    st.pyplot(plt)

