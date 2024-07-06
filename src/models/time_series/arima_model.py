import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from data import db_utils
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
#Statsmodels könyvtár használata a telepítés után. Az ADF teszthez szükséges.
from pmdarima import auto_arima

query = "SELECT timestamp, sleepheartrate FROM sleep_data WHERE sleepheartrate IS NOT NULL"
df = db_utils.fetch_data(query)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Adatok vizualizálása
plt.figure(figsize=(18, 12))
plt.plot(df['sleepheartrate'])
plt.title('Sleep Heart Rate Over Time')
plt.xlabel('Time')
plt.ylabel('Heart Rate')
plt.show()

# Stacionaritás ellenőrzése
result = adfuller(df['sleepheartrate'])
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])

if result[1] > 0.05:
    print("A differenciált idősor nem stacionárius. További differenciálás szükséges.")
else:
    print("A differenciált idősor stacionárius.")
    
model = auto_arima(df['sleepheartrate'], seasonal=False, trace=True)

print(model.summary())

# Előrejelzés
n_periods = 21600  # Például 30 periódusra előrejelzés
forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)
forecast_index = pd.date_range(start=df.index[-1], periods=n_periods, freq='2T')

# Előrejelzések megjelenítése
plt.figure(figsize=(12, 6))
plt.plot(df['sleepheartrate'], label='Historical Data')
plt.plot(forecast_index, forecast, label='Forecast')
plt.fill_between(forecast_index, conf_int[:, 0], conf_int[:, 1], color='pink', alpha=0.3)
plt.title('Sleep Heart Rate Forecast')
plt.xlabel('Time')
plt.ylabel('Heart Rate')
plt.legend()
plt.show()