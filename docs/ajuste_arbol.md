# Ajuste de árboles para estimar el precio de las casas

Este documento resume el proceso ejecutado en
[src/ajuste_arbol.ipynb](../src/ajuste_arbol.ipynb) con el dataset
[data/raw/casas_10000.csv](../data/raw/casas_10000.csv).

## 1. Preparación de datos

Se cargó el archivo `casas_10000.csv` y se definieron las siguientes variables
predictoras:

- `metros`
- `habitaciones`
- `banos`
- `antiguedad`
- `distancia_centro_km`
- `ascensor`
- `terraza`
- `garaje`
- `barrio`
- `tipo`

La variable objetivo fue `precio`.

El preprocesamiento se implementó con un `ColumnTransformer` dentro de un
`Pipeline`:

- `barrio` y `tipo` se codificaron como columnas binarias mediante
  `OneHotEncoder`.
- Las variables numéricas se pasaron sin transformación.
- Se usó `handle_unknown="ignore"` para evitar errores ante categorías nuevas.

Los datos se dividieron en 80 % para entrenamiento y 20 % para prueba usando
`random_state=42`. Las búsquedas de hiperparámetros utilizaron únicamente
`X_train` e `y_train`; el conjunto de prueba se reservó para la evaluación
final.

## 2. Árbol de decisión base

Se entrenó un `DecisionTreeRegressor(random_state=42)` con sus parámetros por
defecto como referencia:

| Modelo | MAE en prueba |
|---|---:|
| Árbol de fábrica | 36.572,00 € |

## 3. Ajuste del árbol de decisión

### Búsqueda aleatoria

Se ejecutó `RandomizedSearchCV` con:

- `n_iter=20`
- `cv=5`
- `scoring="neg_mean_absolute_error"`
- `random_state=42`
- `return_train_score=True`

El espacio explorado fue:

- `max_depth`: `[None, 3, 5, 8, 12, 16, 24]`
- `min_samples_leaf`: `[1, 2, 5, 10, 20, 40]`
- `min_samples_split`: `[2, 5, 10, 20, 40, 80]`

La tabla de resultados convierte el MAE negativo de scikit-learn a positivo y
se ordena de menor a mayor MAE de validación.

### Búsqueda en cuadrícula

Después se ejecutó `GridSearchCV` con `cv=5` y la misma métrica, alrededor de
los valores relevantes encontrados:

- `max_depth`: `[None, 8, 12, 16]`
- `min_samples_leaf`: `[10, 20, 40]`
- `min_samples_split`: `[5, 10, 20, 40]`

El mejor estimador se evaluó una sola vez sobre el conjunto de prueba:

| Modelo | MAE en prueba |
|---|---:|
| Árbol ajustado | 28.655,95 € |

La mejora frente al árbol de fábrica fue:

- Reducción absoluta del MAE: **7.916,05 €**
- Mejora relativa: **21,65 %**

El análisis documentado en el notebook identifica `min_samples_leaf` como el
hiperparámetro que más ayuda a frenar el sobreajuste. `min_samples_split`
apenas cambia el rendimiento en la zona ganadora.

## 4. Parte extra: XGBoost

La biblioteca `xgboost` ya estaba instalada, en la versión `3.4.1`, por lo que
no fue necesario instalarla.

Se entrenó un `XGBRegressor(random_state=42)` de fábrica reutilizando el mismo
`ColumnTransformer` y el mismo `Pipeline` de preprocesamiento.

### Búsqueda aleatoria de XGBoost

Se ejecutó una búsqueda con:

- `n_iter=20`
- `cv=5`
- `scoring="neg_mean_absolute_error"`
- `random_state=42`
- `return_train_score=True`

Los rangos utilizados fueron:

- `n_estimators`: `[50, 100, 200, 400, 800]`
- `learning_rate`: `[0.01, 0.05, 0.1, 0.2, 0.3]`
- `max_depth`: `[2, 3, 5, 7, 10]`
- `subsample`: `[0.6, 0.8, 1.0]`

### Búsqueda en cuadrícula de XGBoost

La cuadrícula se construyó alrededor de la mejor combinación aleatoria. La
mejor configuración obtenida fue:

```text
n_estimators=500
learning_rate=0.05
max_depth=2
subsample=1.0
```

El mejor XGBoost se evaluó una sola vez sobre `X_test` e `y_test`.

## 5. Comparación final

| Modelo | MAE en prueba |
|---|---:|
| Árbol ajustado | 28.655,95 € |
| XGBoost ajustado | 23.722,20 € |

XGBoost sí supera al árbol de decisión ajustado:

- Reducción absoluta del MAE: **4.933,75 €**
- Mejora relativa frente al árbol ajustado: **17,22 %**

## 6. Sobreajuste con una tasa de aprendizaje alta

Se realizó un experimento con una partición de validación interna del conjunto
de entrenamiento. Se compararon estas configuraciones:

- Configuración moderada: `n_estimators=200`,
  `learning_rate=0.05`, `max_depth=3`.
- Configuración agresiva: `n_estimators=800`,
  `learning_rate=0.3`, `max_depth=10`.

Los resultados fueron:

| Configuración | MAE entrenamiento | MAE validación |
|---|---:|---:|
| Moderada | 23.892,12 € | 27.205,50 € |
| Alta tasa / muchas rondas | 1,07 € | 30.605,84 € |

La configuración agresiva reduce casi a cero el error de entrenamiento, pero
empeora el error de validación. Esto demuestra el sobreajuste provocado por
combinar una tasa de aprendizaje alta con muchas rondas y árboles más
profundos.

## 7. Reproducción

Todo el código y las salidas ejecutadas están guardados en
[src/ajuste_arbol.ipynb](../src/ajuste_arbol.ipynb). El notebook fue ejecutado
completo de principio a fin, incluyendo las búsquedas de validación cruzada,
la evaluación final y el experimento de sobreajuste.
