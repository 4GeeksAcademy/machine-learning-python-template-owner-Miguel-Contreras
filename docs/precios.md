# Proceso completo de análisis y modelado de precios

Este documento registra el proceso realizado hasta ahora sobre
[src/precios.ipynb](../src/precios.ipynb), incluyendo los prompts aplicados,
las decisiones tomadas y los resultados obtenidos.

## 1. Exploración inicial del dataset

Prompt aplicado:

> "Carga data/raw/casas_10000.csv. Muéstrame cuántas filas y columnas tiene,
> cuántos valores faltan por columna y cuántas filas duplicadas hay. Haz un
> histograma del precio con una línea en la media y otra en la mediana. Después
> define las características: metros, habitaciones, banos, antiguedad,
> distancia_centro_km, ascensor, terraza, garaje, barrio y tipo. El objetivo es
> precio. No uses id, fecha_publicacion, latitud, longitud ni dias_en_venta.
> trabajamos en src/precios.ipynb"

### Implementación

Se cargó `data/raw/casas_10000.csv` y se definieron:

- Características (`X`):
  `metros`, `habitaciones`, `banos`, `antiguedad`,
  `distancia_centro_km`, `ascensor`, `terraza`, `garaje`, `barrio` y `tipo`.
- Objetivo (`y`): `precio`.
- Columnas excluidas:
  `id`, `fecha_publicacion`, `latitud`, `longitud` y `dias_en_venta`.

Se generó un histograma de `precio` con líneas verticales para la media y la
mediana.

Resultados de calidad de datos:

- Filas: **10.000**
- Columnas: **16**
- Valores faltantes: **0 en todas las columnas**
- Filas duplicadas: **0**

## 2. División de datos y línea base

Prompt aplicado:

> "Separa en entrenamiento (80 %) y prueba (20 %). Calcula la línea base: el
> MAE en la prueba de predecir siempre la mediana del precio de entrenamiento."

### Implementación

Se utilizó `train_test_split` con:

```python
test_size=0.2
random_state=42
```

La línea base predice la mediana de `y_train` para todas las filas de `y_test`.

Resultados:

- Entrenamiento: **8.000 filas**
- Prueba: **2.000 filas**
- Mediana del precio de entrenamiento: **186.000,00 €**
- MAE de la línea base: **108.635,00 €**

## 3. Comparación de modelos con valores por defecto

Prompt aplicado:

> "Compara cuatro modelos con sus valores por defecto: LinearRegression,
> DecisionTreeRegressor, RandomForestRegressor y XGBRegressor. Cada uno va
> dentro de una tubería (Pipeline) con dos pasos: "prep", un
> ColumnTransformer con OneHotEncoder(handle_unknown="ignore") para barrio y
> tipo y remainder="passthrough"; y "model", el modelo. Evalúa cada tubería
> con validación cruzada de 5 partes (KFold mezclado) solo sobre el
> entrenamiento, con el MAE. Muéstrame una tabla con la media, la desviación
> y el tiempo de cada uno, y un gráfico de barras con barras de error."

### Implementación

Cada modelo se envolvió en una tubería con exactamente estos pasos:

1. `prep`: `ColumnTransformer` con `OneHotEncoder(handle_unknown="ignore")`
   para `barrio` y `tipo`, y `remainder="passthrough"`.
2. `model`: el estimador correspondiente.

La evaluación se realizó solo sobre `X_train` e `y_train` con:

```python
KFold(n_splits=5, shuffle=True, random_state=42)
```

La métrica fue el MAE. La tabla incluye la media, la desviación estándar, el
tiempo total de validación y el MAE de cada fold. También se generó un gráfico
de barras con el MAE medio y barras de error correspondientes a la desviación
estándar.

Resultados:

| Modelo | MAE medio | Desviación estándar | Tiempo |
|---|---:|---:|---:|
| `RandomForestRegressor` | 27.642,12 € | 817,83 € | 14,38 s |
| `XGBRegressor` | 27.755,34 € | 627,29 € | 0,85 s |
| `LinearRegression` | 32.994,38 € | 639,26 € | 0,18 s |
| `DecisionTreeRegressor` | 38.393,50 € | 1.339,33 € | 0,31 s |

El mejor MAE medio de esta comparación lo obtuvo `RandomForestRegressor`.

## 4. Búsqueda aleatoria de hiperparámetros

Prompt aplicado:

> "Haz dos RandomizedSearchCV, solo con el entrenamiento, con n_iter=20,
> KFold(5, shuffle=True, random_state=42), scoring
> neg_mean_absolute_error y random_state=42, cada uno sobre la misma tubería
> del paso anterior.
>
> Bosque, con este espacio y en este orden:
> model__n_estimators [100, 200, 300],
> model__max_depth [8, 12, 16, None],
> model__min_samples_leaf [1, 3, 5, 10],
> model__max_features [1.0, 0.5, 0.3].
>
> XGBoost, con este espacio y en este orden:
> model__n_estimators [200, 400, 800],
> model__max_depth [3, 4, 6, 8],
> model__learning_rate [0.03, 0.05, 0.1],
> model__subsample [0.7, 0.85, 1.0],
> model__colsample_bytree [0.7, 1.0],
> model__min_child_weight [1, 5, 10].
>
> Muéstrame, para cada uno, los mejores hiperparámetros, el MAE medio con su
> desviación y el tiempo de la búsqueda."

### Configuración común

Las dos búsquedas utilizaron:

- `RandomizedSearchCV`
- `n_iter=20`
- `KFold(n_splits=5, shuffle=True, random_state=42)`
- `scoring="neg_mean_absolute_error"`
- `random_state=42`
- Solo `X_train` e `y_train`

### RandomForestRegressor

Espacio utilizado:

```python
{
    "model__n_estimators": [100, 200, 300],
    "model__max_depth": [8, 12, 16, None],
    "model__min_samples_leaf": [1, 3, 5, 10],
    "model__max_features": [1.0, 0.5, 0.3],
}
```

Mejores hiperparámetros:

```python
{
    "model__n_estimators": 300,
    "model__min_samples_leaf": 3,
    "model__max_features": 0.5,
    "model__max_depth": None,
}
```

Resultados:

- MAE medio: **26.930,56 €**
- Desviación estándar: **791,57 €**
- Tiempo de búsqueda: **110,78 s**

### XGBRegressor

Espacio utilizado:

```python
{
    "model__n_estimators": [200, 400, 800],
    "model__max_depth": [3, 4, 6, 8],
    "model__learning_rate": [0.03, 0.05, 0.1],
    "model__subsample": [0.7, 0.85, 1.0],
    "model__colsample_bytree": [0.7, 1.0],
    "model__min_child_weight": [1, 5, 10],
}
```

Mejores hiperparámetros:

```python
{
    "model__subsample": 0.85,
    "model__n_estimators": 400,
    "model__min_child_weight": 1,
    "model__max_depth": 4,
    "model__learning_rate": 0.05,
    "model__colsample_bytree": 1.0,
}
```

Resultados:

- MAE medio: **25.762,82 €**
- Desviación estándar: **627,21 €**
- Tiempo de búsqueda: **30,26 s**

En validación cruzada, XGBoost obtuvo el menor MAE medio de las dos búsquedas.

## 5. Archivos y ejecución

El notebook con todo el proceso y sus salidas guardadas está en
[src/precios.ipynb](../src/precios.ipynb).

La documentación relacionada con el ajuste anterior del árbol de decisión
está en [docs/ajuste_arbol.md](ajuste_arbol.md).

Todas las celdas del notebook se ejecutaron de principio a fin después de cada
ampliación, incluyendo:

- Carga y revisión del dataset.
- Histograma de precios.
- Línea base.
- Validación cruzada de cuatro modelos.
- Gráfico de barras con barras de error.
- Las dos búsquedas aleatorias de hiperparámetros.

## 6. Evaluación del mejor XGBoost en prueba

Prompt aplicado:

> "Toma el mejor XGBoost de la búsqueda y mide en la prueba su MAE y su R².
> Haz un gráfico de precio real contra precio predicho con la diagonal, y una
> tabla con el error medio por franja de precio real: hasta 150.000, de
> 150.000 a 300.000, de 300.000 a 600.000 y más de 600.000, con cuántas
> casas hay en cada una. Muéstrame también la predicción más baja. y guarda
> en el .md"

Se tomó `busqueda_xgb.best_estimator_` y se evaluó una sola vez sobre
`X_test`. Se generó un gráfico de precio real frente a precio predicho con la
diagonal de predicción perfecta.

Resultados globales:

- MAE en prueba: **23.791,77 €**
- R² en prueba: **0,9610**
- Predicción más baja: **23.358,40 €**

El error por franja se calculó como el MAE absoluto dentro de cada grupo:

| Franja de precio real | MAE | Casas |
|---|---:|---:|
| Hasta 150.000 € | 17.905,89 € | 770 |
| 150.000–300.000 € | 21.783,47 € | 802 |
| 300.000–600.000 € | 33.948,85 € | 359 |
| Más de 600.000 € | 59.971,29 € | 69 |

## 7. Predicción de casas nuevas

Prompt aplicado:

> "Predice el precio, redondeado a miles, de estas dos casas, pasándolas como
> un DataFrame con los datos crudos:
>
> - 80 m², 3 habitaciones, 1 baño, 20 años, a 2 km del centro, con ascensor,
>   sin terraza ni garaje, barrio Centro, piso.
> - La misma casa en Afueras, a 12 km del centro."

Se construyó un `DataFrame` con las dos casas usando las mismas características
del modelo y se aplicó `busqueda_xgb.best_estimator_`. Las predicciones fueron:

| Casa | Predicción | Predicción redondeada al millar |
|---|---:|---:|
| Centro, 2 km del centro | 243.072,80 € | **243.000 €** |
| Afueras, 12 km del centro | 100.384,77 € | **100.000 €** |

La diferencia entre ambas predicciones refleja el efecto conjunto del barrio y
de la distancia al centro manteniendo el resto de características constante.

## 8. Script reproducible de entrenamiento

Prompt aplicado:

> "Lee src/precio_casas.ipynb. Crea src/train.py, un script que se ejecuta
> desde la raíz del repo, que repita solo lo que quedó decidido: carga
> data/raw/casas_10000.csv con las mismas 10 columnas, separa entrenamiento y
> prueba igual que el notebook, arma la misma tubería con XGBRegressor y los
> mejores hiperparámetros escritos fijos en una constante HIPER, entrena con
> el entrenamiento y muestra la línea base y el MAE en la prueba. Sin
> gráficos, sin búsquedas ni comparaciones. Pon la creación de la tubería en
> una función crear_tuberia()."

No existía `src/precio_casas.ipynb`; se utilizó como referencia
[src/precios.ipynb](../src/precios.ipynb), que contiene el proceso final.

Se creó [src/train.py](../src/train.py), ejecutable desde la raíz del
repositorio. El script:

- Carga `data/raw/casas_10000.csv`.
- Usa las mismas 10 características y `precio` como objetivo.
- Divide los datos con `test_size=0.2` y `random_state=42`.
- Define los hiperparámetros ganadores en la constante `HIPER`.
- Construye la tubería en `crear_tuberia()`.
- Codifica `barrio` y `tipo` con `OneHotEncoder(handle_unknown="ignore")`.
- Entrena únicamente con el conjunto de entrenamiento.
- Muestra la línea base de la mediana y el MAE de XGBoost en prueba.
- No incluye gráficos, búsquedas ni comparaciones adicionales.

Hiperparámetros fijos:

```python
{
    "n_estimators": 400,
    "max_depth": 4,
    "learning_rate": 0.05,
    "subsample": 0.85,
    "colsample_bytree": 1.0,
    "min_child_weight": 1,
}
```

Ejecución verificada desde la raíz:

```text
MAE línea base (mediana): 108,635.00 €
MAE XGBoost en prueba: 23,791.77 €
```

## 9. Validación antes de guardar y corrección del notebook

Se añadió `UMBRAL_MAE = 30_000` a [src/train.py](../src/train.py). Después
de calcular el MAE de prueba, el script solo reentrena con todos los datos y
guarda `models/casas.joblib` si se cumplen ambas condiciones:

- el MAE de prueba no supera `UMBRAL_MAE`;
- el MAE de prueba es menor que el MAE de la línea base.

Si alguna condición falla, muestra un mensaje indicando que no se guarda y
termina antes de crear la carpeta o el archivo del modelo.

También se corrigió la celda de predicción de
[src/precios.ipynb](../src/precios.ipynb) para definir explícitamente
`mejor_xgb = busqueda_xgb.best_estimator_` antes de usarlo, evitando el
`NameError` cuando la celda se ejecuta en un contexto sin esa variable previa.
El notebook completo volvió a ejecutarse correctamente.

## 10. Versionado de modelos y metadata

Prompt aplicado:

> "En src/train.py agrega un argumento de línea de comandos obligatorio
> --version con argparse. El modelo se guarda en
> models/casas_<version>.joblib. Si ese archivo ya existe, el script termina
> sin pisarlo. Junto al modelo guarda
> models/casas_<version>.json con: version, fecha, filas, columnas, modelo,
> hiperparametros, mae_prueba, linea_base y la versión de scikit-learn. y
> guarda todo lo que no se haya guardado en .md"

Se actualizó [src/train.py](../src/train.py) para exigir el argumento:

```bash
python src/train.py --version v1
```

La ejecución crea:

- [models/casas_v1.joblib](../models/casas_v1.joblib)
- [models/casas_v1.json](../models/casas_v1.json)

El JSON incluye la versión, fecha UTC, filas, columnas, modelo,
hiperparámetros, MAE de prueba, línea base y versión de scikit-learn.

Resultados de la versión `v1`:

- Filas: **10.000**
- Columnas: **16**
- Modelo: **XGBRegressor**
- MAE de prueba: **23.791,77 €**
- Línea base: **108.635,00 €**
- Versión de scikit-learn: **1.9.1**
- Tamaño del modelo: **678.223 bytes**
- Tamaño del JSON: **399 bytes**

La protección contra sobrescritura también fue verificada ejecutando de nuevo
el mismo comando. El script terminó con el mensaje:

```text
No se guarda el modelo: ya existe el artefacto de la versión v1.
```
