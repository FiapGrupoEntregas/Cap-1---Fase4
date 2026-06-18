# Cap-1---Fase4



# 🌱 FarmTech Solutions – Fase 4: Previsão Inteligente na Agricultura

Projeto acadêmico que integra **sensores IoT simulados** (ESP32 + Wokwi), **API FastAPI**,
**banco de dados Oracle**, **modelos de Machine Learning** (Scikit-Learn) e um
**dashboard interativo** (Streamlit) para suporte à decisão no agronegócio.

---

## 👨‍🎓 Alunos

- **1** – JonattasFelipe_RM572692
- **2** – NatanaelFilho_RM572474
- **3** – BrunaCamila_RM573402

---


## Links

- Link do vídeo apresentação: [https://youtu.be/QSCSz7Z3c8s](https://youtu.be/QSCSz7Z3c8s)

---

## 📁 Estrutura do Projeto

```
Cap-1---Fase4/
├── iot/                        # Firmware ESP32 (simulação Wokwi)
│   ├── src/main.ino            # Código Arduino/ESP32 dos sensores
│   ├── diagram.json            # Diagrama de conexões no Wokwi
│   └── platformio.ini          # Configuração do PlatformIO
├── src/                        # Backend Python
│   ├── api.py                  # API FastAPI
│   ├── app.py                  # Dashboard Streamlit
│   ├── models/                 # Modelos Pydantic compartilhados
│   │   ├── __init__.py
│   │   └── soil.py
│   ├── core/                   # Pipeline de Machine Learning
│   │   ├── __init__.py
│   │   └── ml_pipeline.py
│   ├── scripts/
│   │   ├── create_table.py     # Cria a tabela no Oracle
│   │   └── delete_table.py     # Remove a tabela no Oracle
│   ├── .env                    # Configurações do banco
│   ├── pyproject.toml          # Dependências gerenciadas pelo uv
│   └── requirements.txt        # Dependências alternativas para pip
├── Data/
│   └── gerar_dados.py          # Gerador de dados sintéticos
└── README.md                   # Este arquivo
```

---

## 🚀 Como Executar

### 1. Configurar o banco de dados

Copie e preencha o arquivo `.env` em `src/.env`:

```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DSN=host:porta/nome_do_servico
```

Exemplo de DSN:

```env
DB_DSN=localhost:1521/XEPDB1
```

### 2. Instalar dependências (com uv)

```bash
cd src
uv sync
```

Ou, se preferir usar o `pip`:

```bash
cd src
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Criar a tabela no banco

```bash
cd src
uv run python scripts/create_table.py
```

Com pip:

```bash
python scripts/create_table.py
```

### 4. Iniciar a API

```bash
cd src
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

A documentação interativa estará disponível em: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Iniciar o dashboard Streamlit

```bash
cd src
uv run streamlit run app.py
```

O dashboard acessa o endpoint `/soil/month/{ano}/{mes}` da API, treina um modelo de regressão com os dados recebidos e exibe métricas, gráficos e previsões.

---

## 🌾 IoT – ESP32 e Sensores de Solo

A pasta `iot/` contém o firmware do ESP32 para coleta dos dados dos sensores.
A simulação é feita no [Wokwi](https://wokwi.com/) a partir do arquivo `diagram.json`.

### Sensores utilizados

| Sensor                              | Pino ESP32 | Variável              | Descrição                           |
|-------------------------------------|------------|-----------------------|-------------------------------------|
| DHT22 (umidade e temperatura do ar) | GPIO 15    | air_humidity          | Umidade relativa do ar (%)          |
| DHT22                               | GPIO 15    | air_temperature       | Temperatura do ar (°C)              |
| Potenciômetro (umidade do solo)     | GPIO 32    | soil_moisture_raw     | Leitura analógica bruta (0-4095)    |
| Potenciômetro (umidade do solo)     | GPIO 32    | soil_moisture_percent | Umidade do solo convertida (%)      |
| Potenciômetro (pH do solo)          | GPIO 33    | ph                    | pH do solo                          |
| Potenciômetro (nitrogênio)          | GPIO 35    | nitrogen              | Nível de nitrogênio                 |
| Potenciômetro (fósforo)             | GPIO 25    | phosphorus            | Nível de fósforo                    |
| Potenciômetro (potássio)            | GPIO 26    | potassium             | Nível de potássio                   |
| LDR (luminosidade)                  | GPIO 34    | light_raw             | Leitura analógica bruta (0-4095)    |
| LDR                                 | GPIO 34    | light_percent         | Luminosidade convertida (%)         |

### Funcionamento do firmware

1. O ESP32 conecta à rede Wi-Fi `Wokwi-GUEST`.
2. A cada `5 segundos`, lê todos os sensores.
3. Imprime os valores no Serial Monitor.
4. Envia os dados em JSON para a API FastAPI via HTTP POST no endpoint `/soil`.

Endpoint configurado no firmware:

```cpp
const char* serverUrl = "http://host.wokwi.internal:8000/soil";
```

### Dependências do firmware

As bibliotecas são declaradas no `platformio.ini`:

```ini
lib_deps =
    adafruit/DHT sensor library @ ^1.4.6
    adafruit/Adafruit Unified Sensor @ ^1.1.14
```

---

## 🔌 Endpoints da API

### `POST /soil`

Insere um novo registro de dados do solo no banco Oracle.

**Corpo da requisição (JSON):**

```json
{
  "air_humidity": 65.5,
  "air_temperature": 24.3,
  "soil_moisture_raw": 512,
  "soil_moisture_percent": 45,
  "ph": 6.8,
  "nitrogen": 12,
  "phosphorus": 8,
  "potassium": 15,
  "light_raw": 1024,
  "light_percent": 78.2,
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

Os campos `latitude` e `longitude` são opcionais.

### `GET /soil`

Lista todos os registros de dados do solo, ordenados do mais recente para o mais antigo.

Parâmetros de consulta:

| Parâmetro | Tipo | Padrão | Descrição                      |
|-----------|------|--------|--------------------------------|
| limit     | int  | 100    | Quantidade máxima de registros |
| offset    | int  | 0      | Número de registros a pular    |

### `GET /soil/{id}`

Retorna um único registro pelo `id`.

### `GET /soil/month/{year}/{month}`

Lista registros filtrados pelo mês e ano do campo `created_at`.

**Exemplo com curl:**

```bash
curl "http://localhost:8000/soil/month/2026/6?limit=10&offset=0"
```

### `POST /simulate`

Insere 200 registros simulados no banco de dados.

```bash
curl -X POST http://localhost:8000/simulate
```

---

## 🧠 Modelos de Machine Learning

O pipeline de regressão está em `src/core/ml_pipeline.py` e suporta:

| Algoritmo             | Tipo          |
|-----------------------|---------------|
| Regressão Linear      | Linear        |
| Random Forest         | Ensemble      |

### Variáveis que podem ser previstas

| Alvo                     | Unidade |
|--------------------------|---------|
| soil_moisture_percent    | %       |
| ph                       | —       |
| nitrogen                 | —       |
| phosphorus               | —       |
| potassium                | —       |
| air_temperature          | °C      |
| air_humidity             | %       |
| light_percent            | %       |

### Métricas Avaliadas

- **MAE** – Erro Absoluto Médio
- **MSE** – Erro Quadrático Médio
- **RMSE** – Raiz do Erro Quadrático Médio
- **R²** – Coeficiente de Determinação

---

## 📊 Dashboard Streamlit

O dashboard `src/app.py` permite:

| Funcionalidade                  | Descrição                                                    |
|---------------------------------|--------------------------------------------------------------|
| Filtro de mês/ano               | Busca dados históricos da API por período                    |
| Escolha do alvo                 | Seleciona qual variável dos sensores será prevista           |
| Escolha do modelo               | Regressão Linear ou Random Forest                            |
| Treinamento                     | Carregamento durante o treino e exibição das métricas        |
| Gráficos                        | Linha Real vs Previsto e barras comparativas                 |
| Previsão para o próximo ciclo   | Predição baseada no último registro recebido                 |

Toda a interface do dashboard está em **português (pt-BR)**.

---

## 📌 Requisitos da Atividade Atendidos

- ✅ **PARTE 1** – Pipeline ML com Scikit-Learn + dashboard Streamlit
- ✅ **PARTE 2** – Regressão múltipla com MAE/MSE/RMSE/R², recomendações de manejo
- ✅ **IR ALÉM 1** – Banco de dados Oracle com ingestão IoT e inserção dinâmica
- ✅ **IR ALÉM 2** – Dashboard analítico com correlações, tendências e previsões interativas

---


## 👨‍💻 Tecnologias

`Python` · `FastAPI` · `OracleDB` · `ESP32` · `Wokwi` · `Scikit-Learn` · `Streamlit` · `Pandas` · `NumPy`

---
