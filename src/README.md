# API de Dados do Solo

API em Python usando [FastAPI](https://fastapi.tiangolo.com/) para receber dados de sensores de solo e armazená-los em um banco Oracle.

## Estrutura do projeto

```
.
├── .env                  # Configurações de conexão com o banco de dados
├── .python-version       # Versão do Python usada pelo uv
├── api.py                 # Aplicação FastAPI
├── create_table.py       # Script para criar a tabela no Oracle
├── delete_table.py       # Script para remover a tabela no Oracle
├── pyproject.toml         # Dependências gerenciadas pelo uv
├── README.md              # Este arquivo
└── requirements.txt       # Dependências alternativas para instalação com pip
```

## Configuração do ambiente

1. Copie o arquivo `.env` e preencha com os dados do seu banco Oracle:

```bash
cp .env .env.local
```

Ou edite diretamente o `.env`:

```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DSN=host:porta/nome_do_servico
```

Exemplo de DSN:

```env
DB_DSN=localhost:1521/XEPDB1
```

## Build com uv (recomendado)

### 1. Instalar o uv

Caso ainda não tenha o `uv` instalado:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Criar o ambiente virtual e instalar dependências

```bash
uv sync
```

### 3. Criar a tabela no banco de dados

```bash
uv run python create_table.py
```

Para remover a tabela, se necessário:

```bash
uv run python delete_table.py
```

### 4. Iniciar a API

```bash
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em: [http://localhost:8000](http://localhost:8000)

Documentação interativa: [http://localhost:8000/docs](http://localhost:8000/docs)

## Build com pip e requirements.txt

Se preferir usar o `pip` em vez do `uv`:

### 1. Criar o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar a tabela no banco de dados

```bash
python create_table.py
```

Para remover a tabela, se necessário:

```bash
python delete_table.py
```

### 4. Iniciar a API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### `POST /soil`

Insere um novo registro de dados do solo no banco de dados.

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

**Exemplo com curl:**

```bash
curl -X POST http://localhost:8000/soil \
  -H "Content-Type: application/json" \
  -d '{
    "air_humidity": 65.5,
    "air_temperature": 24.3,
    "soil_moisture_raw": 512,
    "soil_moisture_percent": 45,
    "ph": 6.8,
    "nitrogen": 12,
    "phosphorus": 8,
    "potassium": 15,
    "light_raw": 1024,
    "light_percent": 78.2
  }'
```

### `GET /soil`

Lista todos os registros de dados do solo, ordenados do mais recente para o mais antigo.

**Parâmetros de consulta:**

| Parâmetro | Tipo | Padrão | Descrição                      |
|-----------|------|--------|--------------------------------|
| limit     | int  | 100    | Quantidade máxima de registros |
| offset    | int  | 0      | Número de registros a pular    |

**Exemplo com curl:**

```bash
curl "http://localhost:8000/soil?limit=10&offset=0"
```

### `GET /soil/{id}`

Retorna um único registro de dados do solo pelo `id`.

**Exemplo com curl:**

```bash
curl http://localhost:8000/soil/1
```

Se o registro não for encontrado, retorna `404 Not Found`.

## Schema da tabela

A tabela `soil_data` é criada com os seguintes campos:

| Coluna                | Tipo          | Descrição                  |
|-----------------------|---------------|----------------------------|
| id                    | NUMBER        | Identificador único (PK)   |
| air_humidity          | BINARY_FLOAT  | Umidade do ar              |
| air_temperature       | BINARY_FLOAT  | Temperatura do ar          |
| soil_moisture_raw     | NUMBER        | Umidade do solo (raw)      |
| soil_moisture_percent | NUMBER        | Umidade do solo (%)        |
| ph                    | BINARY_FLOAT  | pH do solo                 |
| nitrogen              | NUMBER        | Nível de nitrogênio       |
| phosphorus            | NUMBER        | Nível de fósforo          |
| potassium             | NUMBER        | Nível de potássio         |
| light_raw             | NUMBER        | Luminosidade (raw)         |
| light_percent         | BINARY_FLOAT  | Luminosidade (%)           |
| latitude              | BINARY_FLOAT  | Latitude (opcional)        |
| longitude             | BINARY_FLOAT  | Longitude (opcional)       |
| created_at            | TIMESTAMP     | Data/hora de criação       |
| updated_at            | TIMESTAMP     | Data/hora de atualização   |
