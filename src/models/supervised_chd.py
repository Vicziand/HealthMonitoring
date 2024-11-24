import pandas as pd
import streamlit as st
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import xgboost as xgb
from data import db_utils
from sklearn import svm

def create_chd_variables():
    
    conn = db_utils.db_connection()
    query = """
    SELECT "male", "age", "cigsperday", "bpmeds", "prevalentstroke", 
       "prevalenthyp", "diabetes", "heartrate", "bmi", "tenyearchd"
    FROM chd;
    """ 

    data = pd.read_sql(query, conn)
    conn.close()
    
    # Független változók
    x = data[['male', 'age', 'cigsperday', 'bpmeds', 
              'prevalentstroke', 'prevalenthyp', 'diabetes', 'heartrate', 'bmi']]
    
    
    
    # Függő változó
    y = data[['tenyearchd']]
    return x,y

def smote(x,y):
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(x, y)
    return X_res, y_res


def split_data(X_res, y_res):
    # Adatok felosztása tanuló és teszt adatokra (80% tanuló, 20% teszt, randomizációs mag 42 - általánosan használt érték)
    x_train, x_test, y_train, y_test = train_test_split(X_res, y_res, test_size = 0.2, random_state = 42)
    return x_train, x_test, y_train, y_test

def data_scaler(x_train, x_test):
    # Adatok skálázása
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(x_train)
    X_test_scaled = scaler.transform(x_test)
    return X_train_scaled, X_test_scaled, scaler

def data_preprocessing(x,y):
    X_res, y_res = smote(x,y)
    x_train, x_test, y_train, y_test = split_data(X_res, y_res)
    X_train_scaled, X_test_scaled, scaler = data_scaler(x_train, x_test)
    return X_train_scaled, X_test_scaled, scaler, y_train, y_test

def train_log_reg(X_train_scaled, y_train):
    LogRegModel = LogisticRegression()
    LogRegModel.fit(X_train_scaled, y_train.values.ravel())
    return LogRegModel

def train_random_forest(X_train_scaled, y_train):
    RFModel = RandomForestClassifier(n_estimators=200, random_state=42, max_depth= 80, min_samples_split= 8)
    RFModel.fit(X_train_scaled, y_train.values.ravel())
    return RFModel

def train_xgboost(X_train_scaled, y_train, is_chd):
    if is_chd == True:
        XGBModel = xgb.XGBClassifier(colsample_bytree = 0.8, objective='binary:logistic', eval_metric = 'logloss', n_estimators = 200, learning_rate = 0.4, max_depth = 5, subsample = 0.8)
    else:
        XGBModel = xgb.XGBClassifier(colsample_bytree = 0.8, objective='multi:softmax', eval_metric = 'mlogloss', n_estimators = 200, learning_rate = 0.4, max_depth = 5, subsample = 0.8)
    XGBModel.fit(X_train_scaled, y_train.values.ravel())
    return XGBModel

def train_KNN(X_train_scaled, y_train):
    KNN = KNeighborsClassifier(n_neighbors=3, weights='distance', metric='manhattan')
    KNN.fit(X_train_scaled, y_train.values.ravel())
    return KNN

def train_SVM(X_train_scaled, y_train):
    SVMModel = svm.SVC(probability=True, kernel='rbf', C=10, gamma='scale')
    SVMModel.fit(X_train_scaled, y_train.values.ravel())
    return SVMModel

def train_models(X_train_scaled, y_train, is_chd):
    LogRegModel = train_log_reg(X_train_scaled, y_train)
    RFModel = train_random_forest(X_train_scaled, y_train)
    XGBModel = train_xgboost(X_train_scaled, y_train, is_chd)
    KNNModel = train_KNN(X_train_scaled, y_train)
    SVMModel = train_SVM(X_train_scaled, y_train)
    
    models = {
        'Logisztikus Regresszió': LogRegModel,
        'Random Forest': RFModel,
        'XGBoost': XGBModel,
        'K-Nearest Neighbor': KNNModel,
        'Support Vector Machine' : SVMModel
    }
    
    return models

def model_accuracy(model, X_test_scaled, y_test):
    
    y_pred = model.predict(X_test_scaled)
    # Zavarási mátrix és részletes elemzés
    cm = confusion_matrix(y_test, y_pred)
    
    #print(classification_report(y_test, y_pred))

    accuracy = accuracy_score(y_test, y_pred)
    #st.write(f"A modell pontossága: {accuracy * 100:.2f}%")