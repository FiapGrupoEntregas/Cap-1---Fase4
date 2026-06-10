# Cap-1---Fase4
# 🌱 FarmTech Solutions – Fase 4: Previsão Inteligente na Agricultura

Projeto acadêmico que integra **sensores IoT simulados**, **banco de dados SQLite**,
**modelos de Machine Learning** (Scikit-Learn) e um **dashboard interativo** (Streamlit)
para suporte à decisão no agronegócio.

---

## 📁 Estrutura do Projeto

```
farmtech_fase4/
├── app.py                  # Dashboard Streamlit (PARTE 1 + PARTE 2)
├── ml_pipeline.py          # Pipeline de Machine Learning
├── requirements.txt
├── data/
│   ├── gerar_dados.py      # Gerador de dados IoT sintéticos + SQLite
│   ├── dados_agricolas.csv # (gerado automaticamente)
│   └── farmtech.db         # Banco de dados SQLite (gerado automaticamente)
└── models/
    ├── model_rendimento_tha.pkl    # Modelo treinado: rendimento
    ├── model_volume_irrigacao.pkl  # Modelo treinado: irrigação
    ├── model_necessidade_fert.pkl  # Modelo treinado: fertilização
    └── resultados.json             # Métricas comparativas
```

---

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Gerar dados e banco de dados
```bash
python data/gerar_dados.py
```

### 3. Treinar os modelos de ML
```bash
python ml_pipeline.py
```

### 4. Iniciar o dashboard
```bash
streamlit run app.py
```

Acesse em: **http://localhost:8501**

---

## 🧠 Modelos de Machine Learning

Cada variável-alvo é modelada com **4 algoritmos candidatos**:

| Algoritmo             | Tipo          |
|-----------------------|---------------|
| Regressão Linear      | Linear        |
| Ridge Regression      | Linear L2     |
| Random Forest         | Ensemble      |
| Gradient Boosting     | Ensemble      |

O melhor modelo por alvo é selecionado automaticamente com base no **R²** no conjunto de teste.

### Variáveis Previstas
| Alvo                    | Unidade   |
|-------------------------|-----------|
| Rendimento esperado     | ton/ha    |
| Volume de irrigação     | L/m²      |
| Necessidade fertilizante| kg/ha     |

### Métricas Avaliadas
- **MAE** – Erro Absoluto Médio
- **MSE** – Erro Quadrático Médio
- **RMSE** – Raiz do Erro Quadrático Médio
- **R²** – Coeficiente de Determinação

---

## 📊 Páginas do Dashboard

| Página | Conteúdo |
|--------|----------|
| 🏠 Visão Geral | KPIs, arquitetura, estatísticas descritivas |
| 📊 Análise Exploratória | Distribuições, correlações, tendências (Plotly) |
| 🤖 Modelos de ML | Comparativo de algoritmos, Real vs Previsto |
| 🔮 Previsão Interativa | Sliders em tempo real + gauge de rendimento |
| 💡 Recomendações | Diagnóstico automático + projeção de irrigação |
| 🗄️ Banco de Dados | Visualização do SQLite + simulação de nova leitura IoT |

---

## 🌾 Variáveis de Entrada (Sensores IoT)

| Sensor             | Variável          | Unidade  |
|--------------------|-------------------|----------|
| Sensor de umidade  | umidade_solo      | %        |
| Sensor de pH       | ph_solo           | —        |
| Termômetro         | temperatura       | °C       |
| Sensor N           | nitrogenio        | ppm      |
| Sensor P           | fosforo           | ppm      |
| Sensor K           | potassio          | ppm      |
| Piranômetro        | radiacao_solar    | MJ/m²/d  |
| Pluviômetro        | precipitacao      | mm       |

---

## 📌 Requisitos da Atividade Atendidos

- ✅ **PARTE 1** – Pipeline ML com Scikit-Learn + dashboard Streamlit
- ✅ **PARTE 2** – Regressão múltipla com MAE/MSE/RMSE/R², recomendações de manejo
- ✅ **IR ALÉM 1** – Banco de dados SQLite com ingestão IoT e inserção dinâmica
- ✅ **IR ALÉM 2** – Dashboard analítico com correlações, tendências e previsões interativas

---

## 👨‍💻 Tecnologias

`Python` · `Scikit-Learn` · `Streamlit` · `Plotly` · `Pandas` · `NumPy` · `SQLite` · `Joblib`
