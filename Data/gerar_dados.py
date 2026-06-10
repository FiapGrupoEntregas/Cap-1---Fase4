"""
FarmTech Solutions – Gerador de dados agrícolas sintéticos
Simula leituras de sensores IoT: umidade, pH, temperatura, nutrientes, etc.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os

SEED = 42
np.random.seed(SEED)

N_SAMPLES = 500

def gerar_dataset():
    datas = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(N_SAMPLES)]

    umidade_solo   = np.clip(np.random.normal(55, 15, N_SAMPLES), 10, 95)
    ph_solo        = np.clip(np.random.normal(6.2, 0.8, N_SAMPLES), 4.5, 8.5)
    temperatura    = np.clip(np.random.normal(25, 5, N_SAMPLES), 10, 42)
    nitrogenio     = np.clip(np.random.normal(40, 12, N_SAMPLES), 5, 80)
    fosforo        = np.clip(np.random.normal(30, 10, N_SAMPLES), 5, 65)
    potassio       = np.clip(np.random.normal(35, 12, N_SAMPLES), 5, 70)
    radiacao_solar = np.clip(np.random.normal(18, 5, N_SAMPLES), 5, 30)
    precipitacao   = np.clip(np.random.exponential(8, N_SAMPLES), 0, 60)

    # Volume de irrigação (L/m²) – quanto mais seco o solo e quente, mais irriga
    volume_irrigacao = np.clip(
        80 - 0.7 * umidade_solo + 0.5 * temperatura - 0.3 * precipitacao
        + np.random.normal(0, 3, N_SAMPLES),
        0, 50
    )

    # Rendimento (ton/ha) – função de múltiplas variáveis + ruído
    ph_ideal   = 1 - np.abs(ph_solo - 6.5) / 2
    rendimento = (
        2.0
        + 0.04 * umidade_solo
        + 1.5 * ph_ideal
        + 0.05 * nitrogenio
        + 0.03 * fosforo
        + 0.03 * potassio
        + 0.06 * radiacao_solar
        - 0.02 * np.abs(temperatura - 25)
        + np.random.normal(0, 0.4, N_SAMPLES)
    )
    rendimento = np.clip(rendimento, 0.5, 12)

    # Necessidade de fertilização (kg/ha)
    necessidade_fert = np.clip(
        120 - 1.0 * nitrogenio - 0.8 * fosforo - 0.6 * potassio
        + np.random.normal(0, 5, N_SAMPLES),
        0, 100
    )

    cultura = np.random.choice(
        ["Soja", "Milho", "Trigo", "Algodão", "Cana"],
        N_SAMPLES,
        p=[0.35, 0.30, 0.15, 0.12, 0.08]
    )

    df = pd.DataFrame({
        "data":              datas,
        "cultura":           cultura,
        "umidade_solo":      np.round(umidade_solo, 2),
        "ph_solo":           np.round(ph_solo, 2),
        "temperatura":       np.round(temperatura, 2),
        "nitrogenio":        np.round(nitrogenio, 2),
        "fosforo":           np.round(fosforo, 2),
        "potassio":          np.round(potassio, 2),
        "radiacao_solar":    np.round(radiacao_solar, 2),
        "precipitacao":      np.round(precipitacao, 2),
        "volume_irrigacao":  np.round(volume_irrigacao, 2),
        "necessidade_fert":  np.round(necessidade_fert, 2),
        "rendimento_tha":    np.round(rendimento, 3),
    })

    return df


def salvar_sqlite(df, db_path="farmtech.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("leituras_sensores", conn, if_exists="replace", index=False)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS acoes_recomendadas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            data        TEXT,
            cultura     TEXT,
            acao        TEXT,
            valor       REAL,
            unidade     TEXT,
            criado_em   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] {len(df)} registros salvos em {db_path}")


if __name__ == "__main__":
    base = os.path.dirname(__file__)
    df = gerar_dataset()
    csv_path = os.path.join(base, "dados_agricolas.csv")
    db_path  = os.path.join(base, "farmtech.db")
    df.to_csv(csv_path, index=False)
    salvar_sqlite(df, db_path)
    print(f"[CSV] Salvo em {csv_path}")
    print(df.describe())
