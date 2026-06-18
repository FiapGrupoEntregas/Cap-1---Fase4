import os
import random
from datetime import datetime
from typing import List

import oracledb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from models import SoilData, SoilDataResponse

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")


def get_db_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


app = FastAPI()


@app.post("/soil")
def create_soil_data(data: SoilData):
    now = datetime.now()
    payload = data.model_dump()
    payload["created_at"] = now
    payload["updated_at"] = now

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO soil_data (
                        air_humidity,
                        air_temperature,
                        soil_moisture_raw,
                        soil_moisture_percent,
                        ph,
                        nitrogen,
                        phosphorus,
                        potassium,
                        light_raw,
                        light_percent,
                        latitude,
                        longitude,
                        created_at,
                        updated_at
                    ) VALUES (
                        :air_humidity,
                        :air_temperature,
                        :soil_moisture_raw,
                        :soil_moisture_percent,
                        :ph,
                        :nitrogen,
                        :phosphorus,
                        :potassium,
                        :light_raw,
                        :light_percent,
                        :latitude,
                        :longitude,
                        :created_at,
                        :updated_at
                    )
                    """,
                    payload,
                )
            connection.commit()
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"message": "Dados inseridos com sucesso"}


@app.get("/soil", response_model=List[SoilDataResponse])
def list_soil_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        air_humidity,
                        air_temperature,
                        soil_moisture_raw,
                        soil_moisture_percent,
                        ph,
                        nitrogen,
                        phosphorus,
                        potassium,
                        light_raw,
                        light_percent,
                        latitude,
                        longitude,
                        created_at,
                        updated_at
                    FROM soil_data
                    ORDER BY id DESC
                    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
                    """,
                    {"offset": offset, "limit": limit},
                )
                rows = cursor.fetchall()
                columns = [col[0].lower() for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return results


@app.get("/soil/{soil_id}", response_model=SoilDataResponse)
def get_soil_data(soil_id: int):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        air_humidity,
                        air_temperature,
                        soil_moisture_raw,
                        soil_moisture_percent,
                        ph,
                        nitrogen,
                        phosphorus,
                        potassium,
                        light_raw,
                        light_percent,
                        latitude,
                        longitude,
                        created_at,
                        updated_at
                    FROM soil_data
                    WHERE id = :soil_id
                    """,
                    {"soil_id": soil_id},
                )
                row = cursor.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                columns = [col[0].lower() for col in cursor.description]
                result = dict(zip(columns, row))
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result


@app.get("/soil/month/{year}/{month}", response_model=List[SoilDataResponse])
def list_soil_data_by_month(
    year: int,
    month: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mês deve estar entre 1 e 12")

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        air_humidity,
                        air_temperature,
                        soil_moisture_raw,
                        soil_moisture_percent,
                        ph,
                        nitrogen,
                        phosphorus,
                        potassium,
                        light_raw,
                        light_percent,
                        latitude,
                        longitude,
                        created_at,
                        updated_at
                    FROM soil_data
                    WHERE EXTRACT(YEAR FROM created_at) = :year
                      AND EXTRACT(MONTH FROM created_at) = :month
                    ORDER BY id DESC
                    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
                    """,
                    {"year": year, "month": month, "offset": offset, "limit": limit},
                )
                rows = cursor.fetchall()
                columns = [col[0].lower() for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return results


@app.post("/simulate")
def simulate_soil_data():
    now = datetime.now()
    records = []
    for _ in range(200):
        records.append(
            {
                "air_humidity": round(random.uniform(30.0, 90.0), 2),
                "air_temperature": round(random.uniform(15.0, 35.0), 2),
                "soil_moisture_raw": random.randint(0, 1023),
                "soil_moisture_percent": random.randint(0, 100),
                "ph": round(random.uniform(4.0, 9.0), 2),
                "nitrogen": random.randint(0, 255),
                "phosphorus": random.randint(0, 255),
                "potassium": random.randint(0, 255),
                "light_raw": random.randint(0, 1023),
                "light_percent": round(random.uniform(0.0, 100.0), 2),
                "latitude": round(random.uniform(-90.0, 90.0), 6),
                "longitude": round(random.uniform(-180.0, 180.0), 6),
                "created_at": now,
                "updated_at": now,
            }
        )

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO soil_data (
                        air_humidity,
                        air_temperature,
                        soil_moisture_raw,
                        soil_moisture_percent,
                        ph,
                        nitrogen,
                        phosphorus,
                        potassium,
                        light_raw,
                        light_percent,
                        latitude,
                        longitude,
                        created_at,
                        updated_at
                    ) VALUES (
                        :air_humidity,
                        :air_temperature,
                        :soil_moisture_raw,
                        :soil_moisture_percent,
                        :ph,
                        :nitrogen,
                        :phosphorus,
                        :potassium,
                        :light_raw,
                        :light_percent,
                        :latitude,
                        :longitude,
                        :created_at,
                        :updated_at
                    )
                    """,
                    records,
                )
            connection.commit()
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"message": "200 registros simulados inseridos com sucesso"}
