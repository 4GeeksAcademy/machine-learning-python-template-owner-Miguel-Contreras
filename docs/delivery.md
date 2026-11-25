# Proceso completo de análisis y modelado de delivery

Este documento registra el trabajo realizado en
[src/delivery.ipynb](../src/delivery.ipynb) y en
[src/traing2.py](../src/traing2.py), incluyendo los prompts aplicados entre
comillas, las decisiones tomadas y los resultados obtenidos.

## 1. Exploración inicial

Prompt aplicado:

> "Trabajamos en `src/delivery.ipynb`. Carga
> `data/raw/delivery_50000.csv`. Muéstrame cuántas filas y columnas tiene,
> cuántos valores nulos hay por columna, cuántas filas duplicadas completas
> hay y cuántos `id_pedido` están repetidos. Revisa también los valores únicos
> de las columnas de texto (`zona`, `tipo_comida`, `metodo_pago`, `clima`,
> `vehiculo`) para detectar erratas o mayúsculas/minúsculas mezcladas, y
> muestra el mínimo y máximo de todas las columnas numéricas para detectar
> valores imposibles. Finalmente, haz un histograma de `tiempo_real_min` con
> una línea en la media y otra en la mediana"

Se cargó `data/raw/delivery_50000.csv`.

Resultados:

- Filas: **50.180**
- Columnas: **23**
- Filas duplicadas completas: **179**
- `id_pedido` repetidos: **180**
- `id_pedido` distintos afectados por repetición: **180**

Valores nulos:

- `temperatura`: 600
- `repartidores_disponibles`: 301
- `tiempo_real_min`: 3.130
- `llego_tarde`: 3.130
- `calificacion`: 19.482
- Resto de columnas: 0

También se generó el histograma de `tiempo_real_min` con líneas para la media
y la mediana.

## 2. Tablas limpias de categorías y rangos

Prompt aplicado:

> "En `src/delivery.ipynb`, reemplaza o mejora la salida de rangos y
> categorías para que se muestre en dos tablas limpias:
>
> 1. Una tabla con todas las columnas numéricas mostrando su `min`, `max`,
> `media` y `mediana`.
> 2. Una tabla resumen de las columnas categóricas (`zona`, `tipo_comida`,
> `metodo_pago`, `clima`, `vehiculo`) mostrando cuántos valores únicos tiene
> cada una y la lista exacta de esos valores únicos."

Se añadieron dos tablas:

- Tabla numérica con `min`, `max`, `media` y `mediana`.
- Tabla categórica con el número y la lista exacta de valores únicos.

## 3. Salida completa de categorías y rangos `min`/`max`

Prompt aplicado:

> "mprime con un bucle `print(col, sorted(delivery[col].dropna().unique()))`
> para todas las columnas categóricas para que no se corte el texto con
> `...`, y muestra la tabla de `min` y `max` de las columnas numéricas"

La salida completa de categorías se imprimió con un bucle, sin truncamiento:

```text
zona ['Afueras', 'Centro', 'Este', 'Norte', 'Oeste', 'Puerto', 'Sur', 'Universidad']
tipo_comida ['CHINA', 'HAMBURGUESAS', 'MEXICANA', 'PARRILLA', 'PIZZA', 'POSTRES', 'SALUDABLE', 'SUSHI', 'china', 'hamburguesas', 'mexicana', 'parrilla', 'pizza', 'postres', 'saludable', 'sushi']
metodo_pago ['app', 'efectivo', 'tarjeta']
clima ['despejado', 'lluvia', 'nublado', 'tormenta']
vehiculo ['auto', 'bici', 'moto']
```

La tabla numérica `min`/`max` mostró, entre otros valores:

- `distancia_km`: **-6,41** a 18,00
- `importe`: **0,00** a 167,51
- `tiempo_real_min`: 8,00 a **999,00**
- `calificacion`: 1,00 a 5,00

## 4. Conocer los datos

Prompt aplicado:

> "Revisa la salida completa de `valores_unicos` de `zona` y `tipo_comida` y
> la tabla de `min` y `max` de las variables numéricas. Indícame exactamente
> qué categorías están mal escritas (erratas, mayúsculas o espacios) y qué
> columnas numéricas tienen valores imposibles (negativos, ceros o extremos
> irreales). Con todo lo detectado (nulos, 180 `id_pedido` repetidos, erratas
> y valores imposibles), redacta en una celda de texto del notebook la
> respuesta completa a la pregunta **2 · Conocer los datos**"

Se documentó en una celda Markdown:

- La mezcla de mayúsculas/minúsculas en `tipo_comida`:
  - `CHINA`/`china`
  - `HAMBURGUESAS`/`hamburguesas`
  - `MEXICANA`/`mexicana`
  - `PARRILLA`/`parrilla`
  - `PIZZA`/`pizza`
  - `POSTRES`/`postres`
  - `SALUDABLE`/`saludable`
  - `SUSHI`/`sushi`
- No se detectaron espacios sobrantes en las categorías mostradas.
- `distancia_km = -6,41` es imposible.
- `importe = 0,00` es sospechoso para un pedido.
- `tiempo_real_min = 999` es un extremo anómalo o código de error.
- Los ceros de variables binarias, `propina`, `pedidos_previos` y
  `pedidos_activos_zona` son válidos por su significado.

## 5. Limpieza de datos

Prompt aplicado:

> "En `src/delivery.ipynb`, crea una función `limpiar_datos(df)` que aplique
> la limpieza paso a paso y muéstrame cuántas filas quedan tras cada regla:
>
> 1. **Eliminar pedidos no entregados o sin objetivo válido:** Filtra y
> quédate solo con `cancelado == 0` y donde `tiempo_real_min` no sea nulo ni
> sea igual o mayor a `999` (ni menor o igual a `0`).
> 2. **Eliminar duplicados:** Elimina duplicados quedándote con la primera
> aparición de `id_pedido`
> (`drop_duplicates(subset=['id_pedido'], keep='first')`).
> 3. **Normalizar categorías:** Convierte las columnas de texto
> (`tipo_comida`, `zona`, `metodo_pago`, `clima`, `vehiculo`) a minúsculas y
> sin espacios extra (`.str.strip().str.lower()`).
> 4. **Corregir valores imposibles e imputar nulos:** Elimina las filas donde
> `distancia_km <= 0` o `importe <= 0`, e imputa los nulos de `temperatura` y
> `repartidores_disponibles` con su mediana.
> Finalmente, añade una celda de texto **3 · Limpiar los datos** explicando
> cada decisión tomada y cuántas filas finales quedaron."

Se creó `limpiar_datos(df)` y se guardó el resultado en `delivery_limpio`.

| Paso | Filas restantes |
|---|---:|
| Dataset inicial | 50.180 |
| Tras eliminar cancelados y objetivos inválidos | 47.043 |
| Tras eliminar duplicados de `id_pedido` | 46.875 |
| Tras normalizar categorías | 46.875 |
| Tras eliminar `distancia_km <= 0` e `importe <= 0` | 46.857 |
| Tras imputar nulos con la mediana | 46.857 |

La celda **3 · Limpiar los datos** explica estas decisiones y confirma que
`delivery_limpio` contiene **46.857 filas**.

## 6. Ingeniería de fecha, columnas y línea base

Prompt aplicado:

> "En `src/delivery.ipynb`, trabajando sobre `delivery_limpio`:
>
> 1. **Ingeniería básica de fecha:** Convierte `fecha_hora` a tipo datetime y
> extrae las columnas numéricas `hora` (0 a 23) y `dia_semana` (0 a 6).
> 2. **Elegir columnas (Pregunta 4):** Define `y =
> delivery_limpio['tiempo_real_min']`. Para `X`, conserva únicamente las
> columnas conocidas al confirmar el pedido: `zona`, `tipo_comida`,
> `distancia_km`, `cantidad_items`, `importe`, `metodo_pago`, `cliente_nuevo`,
> `pedidos_previos`, `clima`, `temperatura`, `repartidores_disponibles`,
> `pedidos_activos_zona`, `vehiculo`, `tiempo_preparacion_estimado`,
> `tiempo_prometido_min`, `hora` y `dia_semana`."

Se crearon `hora` y `dia_semana`, y se definieron 17 columnas de `X`.

Se excluyeron `id_pedido`, `fecha_hora`, `restaurante_id`,
`tiempo_real_min`, `llego_tarde`, `cancelado`, `propina` y `calificacion`
para evitar identificadores, información posterior al pedido y data leakage.

Prompt aplicado:

> "Separa `X` e `y` en entrenamiento (80%) y prueba (20%) con
> `train_test_split(..., test_size=0.2, random_state=42)`. Calcula la línea
> base sin modelo usando `DummyRegressor(strategy='median')` entrenado en
> `X_train, y_train` y mide su MAE tanto en entrenamiento como en prueba."

Resultados:

- Filas de entrenamiento: **37.485**
- Filas de prueba: **9.372**
- Mediana de entrenamiento: **34,70 min**
- MAE de línea base en entrenamiento: **9,55 min**
- MAE de línea base en prueba: **9,59 min**

## 7. Comparación de modelos y ajuste

Prompt aplicado:

> "En `src/delivery.ipynb`, realiza los pasos 6 y 7 replicando exactamente la
> arquitectura del ejercicio de clase: define un `ColumnTransformer` llamado
> `prep` con `OneHotEncoder(handle_unknown='ignore')` para `zona`,
> `tipo_comida`, `metodo_pago`, `clima`, `vehiculo` y
> `remainder='passthrough'`. Evalúa `LinearRegression`,
> `DecisionTreeRegressor(random_state=42)`,
> `RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)` y
> `XGBRegressor(random_state=42, n_jobs=-1)` dentro de un `Pipeline`."

La validación utilizó `KFold(n_splits=5, shuffle=True, random_state=42)` y
`scoring="neg_mean_absolute_error"` únicamente sobre el entrenamiento.

| Modelo | MAE medio | Desviación | Tiempo |
|---|---:|---:|---:|
| `XGBRegressor` | 4,23 min | 0,04 min | 2,97 s |
| `RandomForestRegressor` | 4,39 min | 0,03 min | 82,79 s |
| `LinearRegression` | 4,79 min | 0,04 min | 3,86 s |
| `DecisionTreeRegressor` | 6,26 min | 0,04 min | 2,11 s |

Prompt aplicado:

> "Ajustar hiperparámetros (Pregunta 7): toma el modelo ganador y ejecuta
> `RandomizedSearchCV` (`n_iter=20`, `KFold(5)`, `scoring='neg_mean_absolute_error'`,
> `random_state=42`, `n_jobs=-1`) explorando al menos `n_estimators`,
> `max_depth`, `learning_rate` y `subsample`/`colsample_bytree`."

Ganó `XGBRegressor`. La mejor configuración fue:

```python
{
    "model__subsample": 0.7,
    "model__n_estimators": 800,
    "model__max_depth": 4,
    "model__learning_rate": 0.05,
    "model__colsample_bytree": 0.7,
}
```

Resultados del ajuste:

- MAE medio ajustado: **4,10 min**
- Desviación estándar ajustada: **0,04 min**
- MAE por defecto: **4,23 min**
- Mejora: **0,13 min**
- La mejora supera la desviación estándar entre folds: **sí**

## 8. Examen final

Prompt aplicado:

> "En `src/delivery.ipynb`, realiza el último paso del notebook
> (**8 · El examen final**): toma el mejor estimador encontrado en la búsqueda
> (`best_estimator_`) y evalúalo una sola vez sobre `X_test` y `y_test`.
> Calcula e imprime con alta precisión el MAE en prueba, además del R² y el
> RMSE. Haz un gráfico de dispersión comparando el tiempo real frente al
> tiempo predicho con la línea diagonal de predicción perfecta. Analiza dónde
> se equivoca más el modelo por `clima`, `vehiculo` y tramos de
> `distancia_km`. Añade la celda de texto **8 · El examen final**."

Resultados:

- MAE en prueba: **4,1032 min**
- R² en prueba: **0,8214**
- RMSE en prueba: **5,2504 min**
- MAE de validación cruzada: **4,10 min**
- MAE de línea base: **9,59 min**

Mayores errores:

- `clima = lluvia`: **4,1856 min**
- `vehiculo = bici`: **4,1729 min**
- `distancia_km > 5`: **4,1173 min**

Se generó el scatter de tiempo real frente a tiempo predicho con la diagonal
de predicción perfecta. Las tres tablas de desglose contienen las columnas
`MAE` y `pedidos`.

Prompt aplicado:

> "En la celda del punto 8 de `src/delivery.ipynb`, renombra la columna
> `casas` a `pedidos` en las tres tablas de desglose de error."

Las tres tablas quedaron actualizadas:

- MAE por clima.
- MAE por vehículo.
- MAE por tramo de distancia.

## 9. Script de producción `traing2.py`

Prompt aplicado:

> "Lee `src/delivery.ipynb` y `src/train.py` (el script de referencia de
> casas). Crea el script **`src/traing2.py`** siguiendo exactamente la misma
> arquitectura y estándares de producción: sin ruido exploratorio, sin
> gráficos, `.head()`, `.describe()` ni `RandomizedSearchCV`; acepta
> `--version` obligatorio; limpia los datos; usa las mismas 17 columnas y
> objetivo; calcula la línea base; usa los hiperparámetros ganadores de
> XGBoost; evalúa la barrera `UMBRAL_MAE = 4.50`; reentrena con el 100 % de
> los datos y guarda el modelo y la metadata."

Se creó [src/traing2.py](../src/traing2.py), ejecutable desde la raíz:

```bash
python src/traing2.py --version v1
```

El script:

- Comprueba con `os.path.exists()` que no exista el modelo versionado.
- Termina con código 1 si la versión ya existe.
- Usa `limpiar_datos(df)`.
- Define `HIPER` con los valores ganadores.
- Usa `DummyRegressor(strategy="median")`.
- Imprime el MAE con cuatro decimales.
- No incluye gráficos, búsquedas ni exploración.
- Reentrena con el 100 % de los datos limpios si supera la barrera.

Resultado verificado:

```text
MAE línea base: 9.5875
MAE en prueba: 4.1032
Modelo guardado en models/delivery_v1.joblib
Metadata guardada en models/delivery_v1.json
```

Archivos generados:

- [models/delivery_v1.joblib](../models/delivery_v1.joblib)
- [models/delivery_v1.json](../models/delivery_v1.json)

La metadata contiene `version`, `fecha_utc`, `filas_entrenamiento`,
`columnas`, `modelo`, `hiperparametros`, `mae_prueba`, `mae_linea_base`,
`umbral_mae` y `version_sklearn`.

Una segunda ejecución de la misma versión fue bloqueada correctamente:

```text
Error: el modelo models/delivery_v1.joblib ya existe; no se sobrescribe.
```

## 10. Artefactos principales

- Notebook ejecutado:
  [src/delivery.ipynb](../src/delivery.ipynb)
- Script de producción:
  [src/traing2.py](../src/traing2.py)
- Modelo versionado:
  [models/delivery_v1.joblib](../models/delivery_v1.joblib)
- Metadata:
  [models/delivery_v1.json](../models/delivery_v1.json)
