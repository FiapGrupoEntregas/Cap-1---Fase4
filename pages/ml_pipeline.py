"""
FarmTech Solutions – Pipeline de Machine Learning (Scikit-Learn)
Treina e avalia modelos de regressão para:
  1. Rendimento esperado (ton/ha)
  2. Volume de irrigação recomendado (L/m²)
  3. Necessidade de fertilização (kg/ha)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE, "data")
MODEL_DIR = os.path.join(BASE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURES = [
    "umidade_solo", "ph_solo", "temperatura",
    "nitrogenio", "fosforo", "potassio",
    "radiacao_solar", "precipitacao", "cultura"
]
NUMERIC = [f for f in FEATURES if f != "cultura"]
CATEGORICAL = ["cultura"]

TARGETS = {
    "rendimento_tha":   "Rendimento (ton/ha)",
    "volume_irrigacao": "Volume de Irrigação (L/m²)",
    "necessidade_fert": "Necessidade de Fertilização (kg/ha)",
}

# ─── helpers ────────────────────────────────────────────────────────────────

def metricas(y_true, y_pred, nome=""):
    mae  = mean_absolute_error(y_true, y_pred)
    mse  = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_true, y_pred)
    if nome:
        print(f"  {nome:30s} | MAE={mae:.4f}  RMSE={rmse:.4f}  R²={r2:.4f}")
    return {"MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2}


def preprocessador():
    return ColumnTransformer([
        ("num", StandardScaler(), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
    ])


def candidatos():
    return {
        "Regressão Linear":     LinearRegression(),
        "Ridge":                Ridge(alpha=1.0),
        "Random Forest":        RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1),
        "Gradient Boosting":    GradientBoostingRegressor(n_estimators=200, learning_rate=0.08, random_state=42),
    }


# ─── treinamento ─────────────────────────────────────────────────────────────

def treinar_todos(df: pd.DataFrame):
    resultados = {}

    for alvo, label in TARGETS.items():
        print(f"\n{'='*60}")
        print(f"  Alvo: {label}")
        print(f"{'='*60}")

        X = df[FEATURES]
        y = df[alvo]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        melhor_r2, melhor_nome, melhor_pipe = -np.inf, None, None
        metricas_alvo = {}

        for nome, modelo in candidatos().items():
            pipe = Pipeline([
                ("prep", preprocessador()),
                ("reg",  modelo),
            ])
            pipe.fit(X_train, y_train)
            y_pred = pipe.predict(X_test)
            m = metricas(y_test, y_pred, nome)
            metricas_alvo[nome] = m
            if m["R2"] > melhor_r2:
                melhor_r2, melhor_nome, melhor_pipe = m["R2"], nome, pipe

        print(f"\n  ✔ Melhor modelo: {melhor_nome}  (R²={melhor_r2:.4f})")

        # salva
        path = os.path.join(MODEL_DIR, f"model_{alvo}.pkl")
        joblib.dump(melhor_pipe, path)

        resultados[alvo] = {
            "label":        label,
            "melhor_modelo": melhor_nome,
            "metricas":     metricas_alvo[melhor_nome],
            "todos":        metricas_alvo,
        }

    # salva métricas em JSON para o dashboard
    with open(os.path.join(MODEL_DIR, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    return resultados


def gerar_graficos(df: pd.DataFrame):
    """Gráficos de correlação salvos como PNG para o dashboard."""
    os.makedirs(os.path.join(BASE, "data"), exist_ok=True)

    # Mapa de correlação
    num_cols = [c for c in df.columns if df[c].dtype in [np.float64, np.int64]]
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(num_cols)))
    ax.set_yticks(range(len(num_cols)))
    ax.set_xticklabels(num_cols, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(num_cols, fontsize=9)
    plt.colorbar(im, ax=ax)
    ax.set_title("Mapa de Correlação – Variáveis Agrícolas", fontsize=13, weight="bold")
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6, color="black")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, "correlacao.png"), dpi=120)
    plt.close()
    print("[OK] correlacao.png gerado")

    # Distribuição do rendimento por cultura
    fig, ax = plt.subplots(figsize=(8, 5))
    culturas = df["cultura"].unique()
    colors = ["#2d8a4e", "#f0a500", "#e05c2a", "#4a90d9", "#9b59b6"]
    for i, c in enumerate(culturas):
        vals = df[df["cultura"] == c]["rendimento_tha"]
        ax.hist(vals, bins=20, alpha=0.65, label=c, color=colors[i % len(colors)])
    ax.set_xlabel("Rendimento (ton/ha)", fontsize=11)
    ax.set_ylabel("Frequência", fontsize=11)
    ax.set_title("Distribuição de Rendimento por Cultura", fontsize=13, weight="bold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, "rendimento_cultura.png"), dpi=120)
    plt.close()
    print("[OK] rendimento_cultura.png gerado")


# ─── main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    csv = os.path.join(DATA_DIR, "dados_agricolas.csv")
    if not os.path.exists(csv):
        from data.gerar_dados import gerar_dataset, salvar_sqlite
        df = gerar_dataset()
        df.to_csv(csv, index=False)
        salvar_sqlite(df, os.path.join(DATA_DIR, "farmtech.db"))
    else:
        df = pd.read_csv(csv)

    treinar_todos(df)
    gerar_graficos(df)
    print("\n[DONE] Modelos e gráficos prontos em ./models/ e ./data/")
