# -*- coding: utf-8 -*-
"""Cortes de luz.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DbObUopp0JMKy9LSHfAM2YaAQwXNfSrU
"""

import matplotlib.pyplot as plt #Gráficas
import pandas as pd #dataframes
from scipy.optimize import curve_fit #curve fitting
import numpy as np #matlab de python
from sklearn import datasets, linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import mean_squared_error, r2_score #MSE función de costo

"""**Base de datos**"""

CortesL=pd.read_csv('Base-de-datos-Econometría.csv')#Lectura de la base de datos
CortesL

"""**Separación de variables**"""

Cortes_x=CortesL.drop(columns=['code_canton','Ventas_AP'])#Variables independientes
Cortes_y=CortesL['Ventas_AP']#Variable dependiente

print(Cortes_x.apply(lambda x: x.value_counts().get(0,0)))#Conteo del número de 0s que aparece en cada columna

print(Cortes_x.apply(lambda x: x.value_counts().get(1,0)))#Conteo del número de 1s que aparece en cada columna

print(len(Cortes_x))#Total de datos

"""**Selección de variables**"""

selector=VarianceThreshold(threshold=0.1)#Identificar variables con varianza mayor a 0.1

selector.fit(Cortes_x)
selector.get_support()#Devolución de características relevantes (True - Var>0.1 y False - Var<0.1)

Cortes_x=Cortes_x.drop(columns=['Coef_Gini','Inflación'])#Eliminar variables

selector.fit(Cortes_x)
selector.get_support()#Comprobación de características relevantes

"""# **Análisis de Datos**

**Estadística descriptiva**
"""

Cortes_Xdf=pd.DataFrame(Cortes_x)
Cortes_Xdf.describe()#Medidas de tendencia central y de dispersión en las variables independientes

Cortes_y=pd.DataFrame(Cortes_y)
Cortes_y.describe()#Medidas de tendencia central y de dispersión en la variable dependiente

"""**Análisis de correlaciones**"""

corr_matrix=Cortes_Xdf.corr()#Matriz de correlación
corr_matrix

import seaborn as sns
plt.figure(figsize=(17, 13))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Matriz de correlación')
plt.show()#Visualización de la correlación en un mapa de calor

Cortes_x=Cortes_x.drop(columns=['Plazas_REEM','Masa_Salarial_REEM','Plazas_AP','Masa_Salarial_AP','Robo_personas'])#Eliminar variables altenamente correlacionadas

plt.figure(figsize=(17, 13))
sns.heatmap(Cortes_x.corr(), annot=True, cmap='coolwarm')
plt.title('Matriz de correlación')
plt.show()#Visualización de la correlación en un mapa de calor

"""**Tratamiento de valores atípicos**"""

Cortes_Xdat=Cortes_x.drop(columns=['year'])
#Creación del diagrama de caja y bigotes
plt.figure(figsize=(8,6))
plt.boxplot(Cortes_Xdat)

# Añadir título y etiquetas
plt.title('Diagrama de Caja y Bigotes')
plt.ylabel('Valor')
plt.xlabel('Variables')

# Mostrar el gráfico
plt.show()

for column in Cortes_Xdat.columns:
  # Calcular los cuartiles
  Q1 = Cortes_Xdat[column].quantile(0.25)
  Q3 = Cortes_Xdat[column].quantile(0.75)
  IQR = Q3 - Q1
  # Definir los límites inferior y superior
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  #Reemplazar valores atípicos con la media
  median_value = Cortes_Xdat[column].median()
  Cortes_Xdat[column] = Cortes_Xdat[column].apply(lambda x: median_value if (x < lower_bound or x > upper_bound) else x)

Cortes_Xdef=Cortes_Xdat#Conjunto de datos definitivo

"""# **Estimación y Diagnóstico**

**Estimación por MCO**
"""

import statsmodels.api as sm
Cortes_Xdef=sm.add_constant(Cortes_Xdef)#Añadir una variable libre (intercepto)
model=sm.OLS(Cortes_y, Cortes_Xdef).fit()#Regresión lineal por mínimos cuadrados ordinarios
print(model.summary())

"""**Pruebas de supuestos clásicos**"""

from scipy import stats
#Prueba de normalidad mediante el test de Shapiro-Wilk
#H0: restos~N(μ,σ)
restos=model.resid
shapiro_test=stats.shapiro(restos)
print('Estadístico de Shapiro-Wilk:', shapiro_test.statistic)
print('Valor p de Shapiro-Wilk:', shapiro_test.pvalue)
if shapiro_test.pvalue > 0.05:#No se rechaza la hipótosis nula
    print('Los residuos siguen una distribución normal.')
else:#Se rechaza hipótesis nula
    print('Los residuos no siguen una distribución normal')

#Prueba de autocorrelación mediante el test de Durbin-Watson
#H0: Restos no tienen correlación
Durbin_Watson_test=sm.stats.durbin_watson(restos)
print('Estadístico de Durbin-Watson:', Durbin_Watson_test)
if Durbin_Watson_test < 1.5:#No se rechaza la hipótesis nula
    print('No hay autocorrelación en los residuos.')
else:#Se rechaza la hipótesis nula
    print('Hay autocorrelación en los residuos.')

"""**Análisis de Multicolinealidad**"""

#Prueba de multicolinealidad mediante el factor de inflación de la varianza
#H0: No hay multicolinealidad
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = pd.DataFrame()
vif["Variables"] = Cortes_Xdef.columns
#Cálculo del vif para cada variable
vif["VIF"] = [variance_inflation_factor(Cortes_Xdef.values, i) for i in range(Cortes_Xdef.shape[1])]
for index, row in vif.iterrows():
    print(f"Variable: {row['Variables']}, VIF: {row['VIF']}")
    if row['VIF'] < 10: #No se rechaza la hipótesis nula
      print('No hay multicolinealidad.')
    else:#Se rechaza la hipótesis nula
      print('Hay multicolinealidad.')
    print('\n')

"""**Detección de heterocedasticidad**"""

#Detección de heterocedasticidad mediante el test de Breusch-Pagan
#H0: Se verifica homecedasticidad
from statsmodels.stats.diagnostic import het_breuschpagan
bp_test=het_breuschpagan(restos, model.model.exog)
print('Estadístico de Breusch-Pagan:', bp_test[0])
print('Valor p de Breusch-Pagan:', bp_test[1])
if bp_test[1] > 0.05:#No se rechaza la hipótesis nula
    print('Se verifica homocedasticidad.')
else:#Se rechaza la hipótesis nula
    print('No se verifica homocedasticidad.')

"""**Pruebas de especificación**"""

#Prueba de especificación mediante el test de Ramsey RESET
#H0: El modelo está correctamento especificado
from statsmodels.stats.diagnostic import linear_reset
reset_test=linear_reset(model,power=2)
print('Estadístico de Ramsey RESET:', reset_test.statistic)
print('Valor p de Ramsey RESET:', reset_test.pvalue)
if reset_test.pvalue > 0.05:#No se rechaza la hipótesis nula
    print('No hay especificación.')
else:#Se rechaza la hipótesis nula
    print('Hay especificación.')

"""**Modelo alterno debido a la heterocedasticidad**"""

# Ajustar el modelo con errores estándar robustos
model_robusto = sm.OLS(Cortes_y, Cortes_Xdef).fit(cov_type='HC3')

# Ver los resultados con errores robustos
print(model_robusto.summary())

"""# **Búsqueda de modelo alterno mediante aprendizaje automático**"""

from sklearn.model_selection import KFold, GridSearchCV #Incluir módulos para validación cruzada y búsqueda de hiperparámetros
from sklearn.preprocessing import StandardScaler#Incluir módulo de estandarización de datos
from sklearn.pipeline import Pipeline#Incluir módulo de proceso en cadena
from sklearn.linear_model import Ridge#Incluir variante de regresión lineal con penalización mediante poderación

"""**Búsqueda de los mejores hiperparámetros para la estimación**"""

#Validación cruzada
kf= KFold(n_splits=5, shuffle=True, random_state=42)#Se considera datos mezclados aleatoriamente con semilla 42 en 5 particiones
#Procesamiento en cadena regresor
pipe = Pipeline([
    ('scaler', StandardScaler()),#Estandarización de datos X~N(0,1)
    ('poly', PolynomialFeatures()),#Características polinomiales
    ('ridge', Ridge())#Regularización R2
])
#Procesamiento en cadena búsqueda de hiperparámetros
param_grid = {
    'poly__degree': [1, 2, 3], #Búsqueda de modelos lineales, cuadráticos y cúbicos
    'ridge__alpha': np.logspace(-2, 2, 1000)#Rango del parámetro de penalización
}
#Buscador de modelo
grid_search=GridSearchCV(pipe,param_grid=param_grid, cv=kf, verbose =2, scoring='r2')#Validación cruzada, salida detallada y métrica R2 para el rendimiento
grid_search.fit(Cortes_Xdef, Cortes_y)#Ajuste del modelo
r2=grid_search.score(Cortes_Xdef, Cortes_y)
best_params=grid_search.best_params_

#Detalle de hiperparámetros obtenidos
best_score=grid_search.best_score_
print('Mejor puntuación de validación cruzada: ', best_score)
print('Hiperparámetros óptimos: ', best_params)
print('R2: ',r2)

"""**Regresor optimizado**"""

from sklearn.metrics import mean_squared_error, r2_score
#Creación del regresor mediante los hiperparámetros encontrados
pipe_Ridge = Pipeline([
    ('scaler', StandardScaler()),#Estandarización de datos
    ('poly', PolynomialFeatures(degree=3)),#Modelo no lineal (cúbico)
    ('ridge', Ridge(alpha=0.04))#Penalización de 0.04 para los coeficientes
])
pipe_Ridge.fit(Cortes_Xdef, Cortes_y)#Ajuste del modelo

y_pred=pipe_Ridge.predict(Cortes_Xdef)#Predicción de la variable
mse=mean_squared_error(Cortes_y, y_pred)#Error cuadrático medio
rmse=np.sqrt(mse)#Raíz cuadrada del error cuadrático medio
r2_f=r2_score(Cortes_y, y_pred)#Cálculo del coeficiente de determinación R2
print('MSE: ',mse)
print('RMSE: ', rmse)
r2_opt = pipe_Ridge.score(Cortes_Xdef, Cortes_y)#R2 optimizado
print('R2: ', r2_opt)

"""**Modelo cúbico**"""

#Gráficos de dispersión
for column in Cortes_Xdef.columns:
    #Crear un gráfico de dispersión para la columna actual vs las ventas
    plt.scatter(Cortes_Xdef[column], Cortes_y)
    plt.xlabel(column)
    plt.ylabel('Ventas_AP')
    plt.show()

#Coeficientes de la regresión cúbica
coef = pipe_Ridge.named_steps['ridge'].coef_#Obtener coeficientes del modelo Ridge
poly_features = pipe_Ridge.named_steps['poly'].get_feature_names_out(input_features=Cortes_Xdef.columns if hasattr(Cortes_Xdef, 'columns') else None)#Obtener nombre de las variables (variables interactivas entre sí)
# Mostrar las características polinomiales y sus coeficientes correspondientes
print("\nCaracterísticas polinomiales generadas:")
for feature, coefficient in zip(poly_features, coef):
    print(f"Característica: {feature}, Coeficiente: {coefficient}")