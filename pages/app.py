"""
FarmTech Solutions – Dashboard Streamlit (Fase 4)
Execute:  streamlit run app.py
"""

import os, json, sqlite3, warnings
warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE, "data")
MODEL_DIR = os.path.join(BASE, "models")
DB_PATH   = os.path.join(DATA_DIR, "farmtech.db")

TARGETS = {
    "rendimento_tha":   "Rendimento (ton/ha)",
    "volume_irrigacao": "Volume de Irrigação (L/m²)",
    "necessidade_fert": "Necessidade de Fertilização (kg/ha)",
}

FEATURES = [
    "umidade_solo", "ph_solo", "temperatura",
    "nitrogenio", "fosforo", "potassio",
    "radiacao_solar", "precipitacao", "cultura"
]

GREEN  = "#2d8a4e"
YELLOW = "#f0a500"
BLUE   = "#1a6fb5"
DARK   = "#1b2631"

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FarmTech Solutions | IA Agrícola",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #f5f7f2; }
    [data-testid="stSidebar"]          { background: #1b2631; }
    [data-testid="stSidebar"] * { color: #ecf0f1 !important; }
    .metric-card {
        background: white; border-radius: 12px; padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,.08);
        border-left: 4px solid #2d8a4e;
    }
    .metric-card h4 { margin: 0 0 4px; font-size: .85rem; color: #666; }
    .metric-card p  { margin: 0; font-size: 1.7rem; font-weight: 700; color: #1b2631; }
    .section-title {
        font-size: 1.25rem; font-weight: 700; color: #1b2631;
        border-bottom: 2px solid #2d8a4e; padding-bottom: 4px; margin: 24px 0 14px;
    }
    .recommendation-box {
        background: #eafaf1; border: 1px solid #27ae60; border-radius: 10px;
        padding: 16px; margin: 8px 0;
    }
    .warning-box {
        background: #fef9e7; border: 1px solid #f39c12; border-radius: 10px;
        padding: 16px; margin: 8px 0;
    }
    .danger-box {
        background: #fdedec; border: 1px solid #e74c3c; border-radius: 10px;
        padding: 16px; margin: 8px 0;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label { font-weight: 600; color: #1b2631; }
</style>
""", unsafe_allow_html=True)

# ─── Data / Model Loaders ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv = os.path.join(DATA_DIR, "dados_agricolas.csv")
    if not os.path.exists(csv):
        from data.gerar_dados import gerar_dataset, salvar_sqlite
        df = gerar_dataset()
        df.to_csv(csv, index=False)
        salvar_sqlite(df, DB_PATH)
    return pd.read_csv(csv, parse_dates=["data"])

@st.cache_resource
def load_models():
    models = {}
    for alvo in TARGETS:
        p = os.path.join(MODEL_DIR, f"model_{alvo}.pkl")
        if os.path.exists(p):
            models[alvo] = joblib.load(p)
    return models

@st.cache_data
def load_resultados():
    p = os.path.join(MODEL_DIR, "resultados.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

def metric_card(title, value, unit=""):
    st.markdown(
        f'<div class="metric-card"><h4>{title}</h4><p>{value} <span style="font-size:.9rem;color:#888">{unit}</span></p></div>',
        unsafe_allow_html=True,
    )

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/sprout.png", width=64)
    st.title("FarmTech Solutions")
    st.caption("Assistente Agrícola Inteligente – Fase 4")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["Visão Geral", "Análise Exploratória", "Modelos de ML",
         "Previsão Interativa", "Recomendações", "Banco de Dados"],
    )
    st.markdown("---")
    st.caption("FarmTech Solutions © 2025\nProjeto Acadêmico – Fase 4")

df      = load_data()
models  = load_models()
results = load_resultados()

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 1 – VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════
if pagina == "Visão Geral":
    st.title("FarmTech Solutions – Fase 4")
    st.subheader("Previsão Inteligente na Agricultura com Machine Learning")

    st.markdown("""
    > **Bem-vindo ao Assistente Agrícola Inteligente.**  
    > Esta plataforma integra dados de sensores IoT, banco de dados relacional e modelos de  
    > Aprendizado de Máquina supervisionado para apoiar gestores na tomada de decisão.
    """)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total de Registros", f"{len(df):,}", "amostras")
    with c2: metric_card("Culturas Monitoradas", df["cultura"].nunique(), "tipos")
    with c3: metric_card("Modelos Treinados", len(models), "pipelines ML")
    with c4:
        best_r2 = max((v["metricas"]["R2"] for v in results.values()), default=0)
        metric_card("Melhor R²", f"{best_r2:.3f}", "")

    st.markdown('<div class="section-title">Visão do Projeto</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Arquitetura da Solução**
        - **Sensores IoT** – Umidade, pH, temperatura, NPK, radiação solar
        - **SQLite** – Persistência e ingestão dos dados coletados  
        - **Scikit-Learn** – Regressão Linear, Ridge, Random Forest, Gradient Boosting  
        - **Streamlit** – Dashboard interativo para gestores  
        - **Sistema de Recomendação** – Ações de irrigação e fertilização  
        """)
    with col_b:
        st.markdown("""
        **Variáveis Previstas**
        | Alvo | Unidade |
        |------|---------|
        | Rendimento esperado | ton/ha |
        | Volume de irrigação | L/m² |
        | Necessidade de fertilização | kg/ha |

        **Métricas Avaliadas:** MAE · MSE · RMSE · R²
        """)

    st.markdown('<div class="section-title">Estatísticas dos Dados</div>', unsafe_allow_html=True)
    st.dataframe(
        df[["umidade_solo","ph_solo","temperatura","rendimento_tha","volume_irrigacao","necessidade_fert"]]
        .describe().round(2),
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 2 – ANÁLISE EXPLORATÓRIA
# ═══════════════════════════════════════════════════════════════════════════
elif pagina == "Análise Exploratória":
    st.title("Análise Exploratória dos Dados")

    tab1, tab2, tab3 = st.tabs(["Distribuições", "Correlações", "Tendências"])

    with tab1:
        col = st.selectbox("Variável", ["umidade_solo","ph_solo","temperatura",
                                         "nitrogenio","fosforo","potassio",
                                         "rendimento_tha","volume_irrigacao","necessidade_fert"])
        fig = px.histogram(df, x=col, color="cultura", barmode="overlay",
                           nbins=40, template="plotly_white",
                           title=f"Distribuição: {col}",
                           color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(legend_title_text="Cultura")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.box(df, x="cultura", y=col, color="cultura",
                      template="plotly_white", title=f"Boxplot por Cultura: {col}",
                      color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        corr = df[num_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdYlGn",
                        zmin=-1, zmax=1, template="plotly_white",
                        title="Mapa de Correlação entre Variáveis Agrícolas",
                        aspect="auto")
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Top correlações com Rendimento (ton/ha)**")
        corr_rend = corr["rendimento_tha"].drop("rendimento_tha").sort_values(ascending=False)
        fig3 = px.bar(x=corr_rend.values, y=corr_rend.index, orientation="h",
                      color=corr_rend.values, color_continuous_scale="RdYlGn",
                      template="plotly_white", labels={"x": "Correlação", "y": ""})
        fig3.update_layout(showlegend=False, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        fig = px.scatter(df, x="umidade_solo", y="rendimento_tha",
                         color="cultura", trendline="ols",
                         template="plotly_white",
                         title="Umidade do Solo × Rendimento",
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(df, x="ph_solo", y="rendimento_tha",
                          color="cultura", trendline="ols",
                          template="plotly_white",
                          title="pH do Solo × Rendimento",
                          color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 3 – MODELOS DE ML
# ═══════════════════════════════════════════════════════════════════════════
elif pagina == "Modelos de ML":
    st.title("Modelos de Machine Learning")

    if not results:
        st.warning("Execute `python ml_pipeline.py` para treinar os modelos primeiro.")
        st.stop()

    for alvo, info in results.items():
        with st.expander(f"{info['label']} — Melhor modelo: **{info['melhor_modelo']}**", expanded=True):
            m = info["metricas"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MAE",  f"{m['MAE']:.4f}")
            c2.metric("MSE",  f"{m['MSE']:.4f}")
            c3.metric("RMSE", f"{m['RMSE']:.4f}")
            c4.metric("R²",   f"{m['R2']:.4f}")

            todos = info.get("todos", {})
            if todos:
                nomes = list(todos.keys())
                r2s   = [todos[n]["R2"]   for n in nomes]
                maes  = [todos[n]["MAE"]  for n in nomes]
                rmses = [todos[n]["RMSE"] for n in nomes]

                fig = make_subplots(rows=1, cols=3,
                                    subplot_titles=["R² (maior = melhor)",
                                                    "MAE (menor = melhor)",
                                                    "RMSE (menor = melhor)"])
                kw = dict(marker_color=[GREEN, BLUE, YELLOW, "#e74c3c"])
                fig.add_trace(go.Bar(x=nomes, y=r2s,   name="R²",   **kw), 1, 1)
                fig.add_trace(go.Bar(x=nomes, y=maes,  name="MAE",  **kw), 1, 2)
                fig.add_trace(go.Bar(x=nomes, y=rmses, name="RMSE", **kw), 1, 3)
                fig.update_layout(showlegend=False, height=320, template="plotly_white",
                                  title_text="Comparativo de Modelos Candidatos")
                st.plotly_chart(fig, use_container_width=True)

            if alvo in models:
                model = models[alvo]
                X = df[FEATURES]
                y = df[alvo]
                _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                y_pred = model.predict(X_test)
                fig2 = px.scatter(x=y_test, y=y_pred, labels={"x": "Real", "y": "Previsto"},
                                  template="plotly_white",
                                  title=f"Real × Previsto – {info['label']}",
                                  opacity=0.6, color_discrete_sequence=[GREEN])
                mn, mx = float(y_test.min()), float(y_test.max())
                fig2.add_shape(type="line", x0=mn, y0=mn, x1=mx, y1=mx,
                               line=dict(color="red", dash="dash", width=1.5))
                st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 4 – PREVISÃO INTERATIVA
# ═══════════════════════════════════════════════════════════════════════════
elif pagina == "Previsão Interativa":
    st.title("Previsão em Tempo Real")
    st.info("Ajuste os parâmetros do sensor e clique em **Gerar Previsão** para obter estimativas instantâneas.")

    if not models:
        st.warning("Execute `python ml_pipeline.py` para treinar os modelos primeiro.")
        st.stop()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Parâmetros do Campo")
        cultura   = st.selectbox("Cultura", ["Soja", "Milho", "Trigo", "Algodão", "Cana"])
        umidade   = st.slider("Umidade do Solo (%)", 10.0, 95.0, 55.0, 0.5)
        ph        = st.slider("pH do Solo", 4.5, 8.5, 6.5, 0.1)
        temp      = st.slider("Temperatura (°C)", 10.0, 42.0, 25.0, 0.5)
        precip    = st.slider("Precipitação (mm)", 0.0, 60.0, 8.0, 0.5)

    with col2:
        st.markdown("### Nutrientes e Radiação")
        n_val  = st.slider("Nitrogênio (ppm)", 5.0, 80.0, 40.0, 1.0)
        p_val  = st.slider("Fósforo (ppm)",    5.0, 65.0, 30.0, 1.0)
        k_val  = st.slider("Potássio (ppm)",   5.0, 70.0, 35.0, 1.0)
        rad    = st.slider("Radiação Solar (MJ/m²/dia)", 5.0, 30.0, 18.0, 0.5)

    if st.button("Gerar Previsão", type="primary", use_container_width=True):
        entrada = pd.DataFrame([{
            "umidade_solo": umidade, "ph_solo": ph, "temperatura": temp,
            "nitrogenio": n_val, "fosforo": p_val, "potassio": k_val,
            "radiacao_solar": rad, "precipitacao": precip, "cultura": cultura,
        }])

        st.markdown("---")
        st.markdown("### Resultados da Previsão")

        cols = st.columns(3)
        labels = {
            "rendimento_tha":   ("Rendimento", "ton/ha"),
            "volume_irrigacao": ("Irrigação",  "L/m²"),
            "necessidade_fert": ("Fertilizante","kg/ha"),
        }
        prevs = {}
        for i, (alvo, (nome, unit)) in enumerate(labels.items()):
            if alvo in models:
                val = float(models[alvo].predict(entrada)[0])
                prevs[alvo] = val
                with cols[i]:
                    st.metric(nome, f"{val:.2f} {unit}")

        if "rendimento_tha" in prevs:
            rend = prevs["rendimento_tha"]
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=rend,
                title={"text": "Rendimento Previsto (ton/ha)"},
                delta={"reference": df["rendimento_tha"].mean()},
                gauge={
                    "axis": {"range": [0, 12]},
                    "bar":  {"color": GREEN},
                    "steps": [
                        {"range": [0,   4],  "color": "#fadbd8"},
                        {"range": [4,   7],  "color": "#fef9e7"},
                        {"range": [7,  12],  "color": "#eafaf1"},
                    ],
                    "threshold": {"line": {"color": "red","width": 3}, "value": 3},
                },
                number={"suffix": " t/ha"},
            ))
            fig.update_layout(height=300, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 5 – RECOMENDAÇÕES
# ═══════════════════════════════════════════════════════════════════════════
elif pagina == "Recomendações":
    st.title("Sistema de Recomendações Agrícolas")
    st.info("Insira os valores atuais do campo para receber recomendações automáticas de manejo.")

    if not models:
        st.warning("Execute `python ml_pipeline.py` primeiro.")
        st.stop()

    with st.form("form_rec"):
        c1, c2, c3 = st.columns(3)
        with c1:
            cultura = st.selectbox("Cultura", ["Soja","Milho","Trigo","Algodão","Cana"])
            umidade = st.number_input("Umidade (%)",       10.0, 95.0, 55.0, 1.0)
            ph      = st.number_input("pH",                 4.5,  8.5,  6.5, 0.1)
        with c2:
            temp    = st.number_input("Temperatura (°C)",  10.0, 42.0, 25.0, 0.5)
            precip  = st.number_input("Precipitação (mm)",  0.0, 60.0,  8.0, 0.5)
            rad     = st.number_input("Radiação (MJ/m²/d)", 5.0, 30.0, 18.0, 0.5)
        with c3:
            n_val   = st.number_input("Nitrogênio (ppm)",   5.0, 80.0, 40.0, 1.0)
            p_val   = st.number_input("Fósforo (ppm)",      5.0, 65.0, 30.0, 1.0)
            k_val   = st.number_input("Potássio (ppm)",     5.0, 70.0, 35.0, 1.0)
        submitted = st.form_submit_button("Analisar Campo", type="primary", use_container_width=True)

    if submitted:
        entrada = pd.DataFrame([{
            "umidade_solo": umidade, "ph_solo": ph, "temperatura": temp,
            "nitrogenio": n_val, "fosforo": p_val, "potassio": k_val,
            "radiacao_solar": rad, "precipitacao": precip, "cultura": cultura,
        }])

        irrig = float(models["volume_irrigacao"].predict(entrada)[0]) if "volume_irrigacao" in models else 0
        fert  = float(models["necessidade_fert"].predict(entrada)[0]) if "necessidade_fert" in models else 0
        rend  = float(models["rendimento_tha"].predict(entrada)[0])   if "rendimento_tha"   in models else 0

        st.markdown("---")
        st.markdown("### Diagnóstico e Recomendações")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rendimento Previsto",     f"{rend:.2f} ton/ha")
        c2.metric("Irrigação Recomendada",   f"{irrig:.1f} L/m²")
        c3.metric("Fertilizante Necessário", f"{fert:.1f} kg/ha")

        recs = []
        if umidade < 35:
            recs.append(("danger", "⚠ Déficit Hídrico Crítico",
                         f"Umidade em {umidade:.1f}%. Irrigar imediatamente com ~{irrig:.1f} L/m². "
                         "Risco elevado de perda de produtividade."))
        elif umidade < 50:
            recs.append(("warning", "Umidade Abaixo do Ideal",
                         f"Umidade em {umidade:.1f}%. Considere irrigação de {irrig:.1f} L/m² "
                         "nas próximas 48h para manter produtividade."))
        else:
            recs.append(("ok", "Umidade Adequada",
                         f"Umidade em {umidade:.1f}%. Nível satisfatório. "
                         "Monitorar a cada 24h."))

        if ph < 5.5:
            recs.append(("danger", "⚠ Solo Muito Ácido",
                         f"pH {ph:.1f} – Aplicar calcário para elevar o pH entre 6.0 e 7.0. "
                         "pH ácido reduz absorção de nutrientes."))
        elif ph > 7.5:
            recs.append(("warning", "Solo Alcalino",
                         f"pH {ph:.1f} – Considere aplicação de enxofre ou matéria orgânica "
                         "para reduzir o pH gradualmente."))
        else:
            recs.append(("ok", "pH Ideal",
                         f"pH {ph:.1f} – Dentro da faixa ideal (5.5–7.5). "
                         "Condições favoráveis à absorção de nutrientes."))

        if fert > 60:
            recs.append(("danger", "⚠ Deficiência Nutricional Severa",
                         f"Necessidade de {fert:.1f} kg/ha de fertilizante NPK. "
                         "Realizar adubação corretiva urgente."))
        elif fert > 30:
            recs.append(("warning", "Fertilização Recomendada",
                         f"Aplicar ~{fert:.1f} kg/ha de NPK balanceado "
                         "antes do próximo ciclo de crescimento."))
        else:
            recs.append(("ok", "Nutrição Adequada",
                         "Níveis de NPK satisfatórios. Monitorar mensalmente."))

        if temp > 35:
            recs.append(("danger", "⚠ Estresse Térmico",
                         f"Temperatura em {temp:.1f}°C. Considere irrigação noturna "
                         "para resfriamento do dossel e redução do estresse."))
        elif temp < 15:
            recs.append(("warning", "Temperatura Baixa",
                         f"Temperatura em {temp:.1f}°C. Risco de geada em culturas sensíveis. "
                         "Monitorar previsão do tempo."))

        boxes = {"ok": "recommendation-box", "warning": "warning-box", "danger": "danger-box"}
        for tipo, titulo, texto in recs:
            st.markdown(
                f'<div class="{boxes[tipo]}"><strong>{titulo}</strong><br>{texto}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### Projeção de Rendimento com Irrigação")
        volumes = np.linspace(0, 50, 40)
        rendimentos = []
        for v in volumes:
            e = entrada.copy()
            um_sim = min(95, umidade + v * 0.4)
            e["umidade_solo"] = um_sim
            if "rendimento_tha" in models:
                rendimentos.append(float(models["rendimento_tha"].predict(e)[0]))
            else:
                rendimentos.append(rend)

        fig = px.line(x=volumes, y=rendimentos,
                      labels={"x": "Volume de Irrigação (L/m²)", "y": "Rendimento Previsto (ton/ha)"},
                      template="plotly_white", title="Impacto da Irrigação no Rendimento")
        fig.update_traces(line_color=GREEN, line_width=2.5)
        fig.add_vline(x=irrig, line_dash="dash", line_color="red",
                      annotation_text=f"Recomendado: {irrig:.1f} L/m²")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA 6 – BANCO DE DADOS
# ═══════════════════════════════════════════════════════════════════════════
elif pagina == "Banco de Dados":
    st.title("Banco de Dados – Ingestão IoT")

    st.markdown("""
    Visualize os dados armazenados no banco SQLite, simulando a ingestão contínua  
    de leituras provenientes dos sensores IoT conectados ao campo.
    """)

    tab1, tab2 = st.tabs(["Dados Armazenados", "Simular Nova Leitura"])

    with tab1:
        cultura_f = st.multiselect("Filtrar por Cultura", df["cultura"].unique().tolist(),
                                   default=df["cultura"].unique().tolist())
        df_f = df[df["cultura"].isin(cultura_f)].sort_values("data", ascending=False)
        st.dataframe(df_f.head(100).reset_index(drop=True), use_container_width=True)
        st.caption(f"Exibindo {min(100, len(df_f))} de {len(df_f)} registros.")

        csv_bytes = df_f.to_csv(index=False).encode("utf-8")
        st.download_button("Exportar CSV", csv_bytes, "farmtech_dados.csv", "text/csv")

    with tab2:
        st.info("Simule a inserção de uma nova leitura de sensor no banco de dados.")
        with st.form("nova_leitura"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nl_cult  = st.selectbox("Cultura", ["Soja","Milho","Trigo","Algodão","Cana"], key="nl_cult")
                nl_um    = st.number_input("Umidade (%)",   10.0, 95.0, 55.0, key="nl_um")
                nl_ph    = st.number_input("pH",             4.5,  8.5,  6.5, key="nl_ph")
            with c2:
                nl_temp  = st.number_input("Temp (°C)",    10.0, 42.0, 25.0, key="nl_temp")
                nl_n     = st.number_input("N (ppm)",        5.0, 80.0, 40.0, key="nl_n")
                nl_p     = st.number_input("P (ppm)",        5.0, 65.0, 30.0, key="nl_p")
            with c3:
                nl_k     = st.number_input("K (ppm)",        5.0, 70.0, 35.0, key="nl_k")
                nl_rad   = st.number_input("Radiação",        5.0, 30.0, 18.0, key="nl_rad")
                nl_prec  = st.number_input("Precipit. (mm)", 0.0, 60.0,  8.0, key="nl_prec")
            ins = st.form_submit_button("Inserir no Banco de Dados", type="primary")

        if ins:
            from datetime import datetime
            nova = pd.DataFrame([{
                "data": datetime.now().strftime("%Y-%m-%d"),
                "cultura": nl_cult, "umidade_solo": nl_um, "ph_solo": nl_ph,
                "temperatura": nl_temp, "nitrogenio": nl_n, "fosforo": nl_p,
                "potassio": nl_k, "radiacao_solar": nl_rad, "precipitacao": nl_prec,
                "volume_irrigacao": 0.0, "necessidade_fert": 0.0, "rendimento_tha": 0.0,
            }])
            conn = sqlite3.connect(DB_PATH)
            nova.to_sql("leituras_sensores", conn, if_exists="append", index=False)
            conn.close()
            st.success("Leitura inserida com sucesso no banco de dados SQLite.")
            st.balloons()
