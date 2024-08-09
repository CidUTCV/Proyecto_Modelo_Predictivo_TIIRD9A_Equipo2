# 
from unittest import result
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.calibration import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit, train_test_split
from scipy import stats
# 
import tkinter as tk
from tkinter import ttk
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
import lightgbm as lgb
# 
from sklearn.model_selection import KFold
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor, GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.linear_model import LogisticRegression
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBRFClassifier, XGBRegressor
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score, classification_report, precision_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Cargar el dataset
# NOTA: Cambiar ruta de acuerdo a la del usuario
df = pd.read_csv('C:/Users/joseg/OneDrive/Documentos/LAP NICKOLE/CASO PRÁCTICO/Códigos/Datasets/data.csv')

# Convertir 'Date' a formato datetime
df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y")

# Extraer componentes de fecha
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day

# Convertir 'Complete Hour' a formato datetime
df['Complete_Hour'] = pd.to_datetime(df['Complete_Hour'], format="%H:%M:%S")

# Extraer componentes de hora y minuto
df['Hour'] = df['Complete_Hour'].dt.hour
df['Minute'] = df['Complete_Hour'].dt.minute
df['Second'] = df['Complete_Hour'].dt.second

# Convertir a variables categóricas y reescribir como variables numéricas
df['Year'] = pd.Categorical(df['Year'], categories=range(2000, 2030), ordered=True)
df['Month'] = pd.Categorical(df['Month'], categories=range(1, 13), ordered=True)
df['Day'] = pd.Categorical(df['Day'], categories=range(1, 32), ordered=True)
df['Hour'] = pd.Categorical(df['Hour'], categories=range(24), ordered=True)
df['Minute'] = pd.Categorical(df['Minute'], categories=range(60), ordered=True)
df['Second'] = pd.Categorical(df['Second'], categories=range(60), ordered=True)

# Verificar la presencia de las columnas antes de cualquier procesamiento adicional
print("Columnas antes de eliminar duplicados o valores atípicos:")
print(df.columns)

# Eliminar columnas originales si no las necesitas
categorical_df = df.drop(columns=['Date', 'Complete_Hour'])

# Obtener la cantidad de valores únicos en cada columna
unique_counts = categorical_df.nunique()

# Seleccionar las columnas con un solo valor único
#columns_to_drop = unique_counts[unique_counts == 1].index
columns_to_drop = unique_counts[(unique_counts == 1) & (~unique_counts.index.isin(['Year', 'Month']))].index

# Eliminar las columnas con un solo valor único
categorical_df = categorical_df.drop(columns=columns_to_drop)

# Eliminar filas duplicadas basadas en todas las columnas
categorical_df = categorical_df.drop_duplicates()


# Verificar las columnas después de eliminar duplicados
print("Columnas después de eliminar duplicados:")
print(categorical_df.columns)

# Lista de columnas en las que deseas eliminar valores atípicos
columns_to_filter = ['PM2.5', 'CO2', 'TVOC', 'O3', 'CO', 'NO2', 'temperature', 'humidity']

# Definir un umbral para identificar valores atípicos (por ejemplo, 3)
threshold = 3

# Almacenar índices antes de la eliminación
indices_originales = categorical_df.index.tolist()

# Crear un DataFrame vacío para almacenar los valores eliminados
valores_eliminados = pd.DataFrame()

# Filtrar el DataFrame para excluir valores atípicos en cada columna
for column in columns_to_filter:
    z_scores = stats.zscore(categorical_df[column])
    filas_eliminadas = categorical_df[(z_scores >= threshold) | (z_scores <= -threshold)]
    valores_eliminados = pd.concat([valores_eliminados, filas_eliminadas])

# Eliminar filas duplicadas de valores_eliminados
valores_eliminados = valores_eliminados.drop_duplicates()

# Obtener índices después de la eliminación
indices_despues_de_eliminar = categorical_df.index.tolist()

# Obtener los índices de las filas eliminadas
indices_eliminados = list(set(indices_originales) - set(indices_despues_de_eliminar))

# Imprimir los índices de las filas eliminadas y sus valores
print("Índices de filas eliminadas:", indices_eliminados)
print("Valores eliminados:")
print(valores_eliminados)

# Establecer umbrales para cada contaminante (por ejemplo, 50 para CO2)
umbral_CO2 = 415    # Establece el umbral adecuado para CO2
umbral_PM25 = 74    # Establece el umbral adecuado para PM2.5
umbral_TVOC = 940   # Establece el umbral adecuado para TVOC
umbral_O3 = 0.600   # Establece el umbral adecuado para O3
umbral_CO = 50      # Establece el umbral adecuado para CO
umbral_NO2 = 2      # Establece el umbral adecuado para NO2

# Función para asignar 1 si es malo, 0 si es bueno
def asignar_estado(valor, umbral):
    if valor > umbral:
        return 1  # Malo
    else:
        return 0  # Bueno

# Aplicar la función a cada columna y crear nuevas columnas binarias
categorical_df['value_CO2'] = categorical_df['CO2'].apply(lambda x: asignar_estado(x, umbral_CO2))
categorical_df['value_PM25'] = categorical_df['PM2.5'].apply(lambda x: asignar_estado(x, umbral_PM25))
categorical_df['value_TVOC'] = categorical_df['TVOC'].apply(lambda x: asignar_estado(x, umbral_TVOC))
categorical_df['value_O3'] = categorical_df['O3'].apply(lambda x: asignar_estado(x, umbral_O3))
categorical_df['value_CO'] = categorical_df['CO'].apply(lambda x: asignar_estado(x, umbral_CO))
categorical_df['value_NO2'] = categorical_df['NO2'].apply(lambda x: asignar_estado(x, umbral_NO2))

df_pm25 = categorical_df[['PM2.5', 'value_PM25']]
df_CO2 = categorical_df[['CO2', 'value_CO2']]
df_TVOC = categorical_df[['TVOC', 'value_TVOC']]
df_O3 = categorical_df[['O3', 'value_O3']]
df_CO = categorical_df[['CO', 'value_CO']]
df_NO2 = categorical_df[['NO2', 'value_NO2']]

# Asegurarse de que las columnas 'Year' y 'Month' estén en el DataFrame
if 'Year' not in categorical_df.columns or 'Month' not in categorical_df.columns:
    print("Las columnas 'Year' y 'Month' no están en el DataFrame.")
    print(categorical_df.columns)
    raise KeyError("Las columnas 'Year' y 'Month' no están en el DataFrame.")

#########################################################
######################## PM 2.5 #########################
#########################################################



#########################################################
########################## ... ##########################
#########################################################


