import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


FEATURES = [
    "zona",
    "tipo_comida",
    "distancia_km",
    "cantidad_items",
    "importe",
    "metodo_pago",
    "cliente_nuevo",
    "pedidos_previos",
    "clima",
    "temperatura",
    "repartidores_disponibles",
    "pedidos_activos_zona",
    "vehiculo",
    "tiempo_preparacion_estimado",
    "tiempo_prometido_min",
    "hora",
    "dia_semana",
]
TARGET = "tiempo_real_min"
VARIABLES_CATEGORICAS = ["zona", "tipo_comida", "metodo_pago", "clima", "vehiculo"]
HIPER = {
    "n_estimators": 800,
    "max_depth": 4,
    "learning_rate": 0.05,
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "random_state": 42,
    "n_jobs": -1,
}
UMBRAL_MAE = 4.50


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el dataset y añade las variables básicas de fecha."""
    limpio = df.copy()
    limpio = limpio[
        (limpio["cancelado"] == 0)
        & limpio["tiempo_real_min"].notna()
        & (limpio["tiempo_real_min"] < 999)
        & (limpio["tiempo_real_min"] > 0)
    ].copy()
    limpio = limpio.drop_duplicates(subset=["id_pedido"], keep="first").copy()

    columnas_texto = ["tipo_comida", "zona", "metodo_pago", "clima", "vehiculo"]
    for columna in columnas_texto:
        limpio[columna] = limpio[columna].str.strip().str.lower()

    limpio = limpio[(limpio["distancia_km"] > 0) & (limpio["importe"] > 0)].copy()
    for columna in ["temperatura", "repartidores_disponibles"]:
        limpio[columna] = limpio[columna].fillna(limpio[columna].median())

    limpio["fecha_hora"] = pd.to_datetime(limpio["fecha_hora"])
    limpio["hora"] = limpio["fecha_hora"].dt.hour
    limpio["dia_semana"] = limpio["fecha_hora"].dt.day_of_week
    return limpio


def crear_tuberia() -> Pipeline:
    """Crea la tubería fija de preprocesamiento y XGBoost."""
    prep = ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OneHotEncoder(handle_unknown="ignore"),
                VARIABLES_CATEGORICAS,
            )
        ],
        remainder="passthrough",
    )
    return Pipeline(
        [
            ("prep", prep),
            ("model", XGBRegressor(**HIPER)),
        ]
    )


def main(version: str) -> None:
    model_path = Path(f"models/delivery_{version}.joblib")
    metadata_path = Path(f"models/delivery_{version}.json")
    if os.path.exists(model_path):
        print(
            f"Error: el modelo {model_path} ya existe; "
            "no se sobrescribe."
        )
        sys.exit(1)

    houses = pd.read_csv("data/raw/delivery_50000.csv")
    delivery_limpio = limpiar_datos(houses)
    X = delivery_limpio[FEATURES]
    y = delivery_limpio[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    linea_base = DummyRegressor(strategy="median")
    linea_base.fit(X_train, y_train)
    mae_linea_base = mean_absolute_error(y_test, linea_base.predict(X_test))

    tuberia = crear_tuberia()
    tuberia.fit(X_train, y_train)
    mae_prueba = mean_absolute_error(y_test, tuberia.predict(X_test))
    print(f"MAE línea base: {mae_linea_base:.4f}")
    print(f"MAE en prueba: {mae_prueba:.4f}")

    if mae_prueba > UMBRAL_MAE or mae_prueba >= mae_linea_base:
        print("El modelo no supera la barrera de calidad; no se guarda.")
        sys.exit(1)

    tuberia_final = crear_tuberia()
    tuberia_final.fit(X, y)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(tuberia_final, model_path)

    metadata = {
        "version": version,
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "filas_entrenamiento": int(len(X)),
        "columnas": FEATURES,
        "modelo": "XGBRegressor",
        "hiperparametros": HIPER,
        "mae_prueba": float(mae_prueba),
        "mae_linea_base": float(mae_linea_base),
        "umbral_mae": UMBRAL_MAE,
        "version_sklearn": sklearn.__version__,
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Modelo guardado en {model_path}")
    print(f"Metadata guardada en {metadata_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrena y versiona el modelo de delivery."
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Identificador obligatorio de la versión, por ejemplo v1.",
    )
    args = parser.parse_args()
    main(args.version)
