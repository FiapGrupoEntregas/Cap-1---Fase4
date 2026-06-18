import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import oracledb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")


def get_db_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


class SoilData(BaseModel):
    air_humidity: float
    air_temperature: float
    soil_moisture_raw: int
    soil_moisture_percent: int
    ph: float
    nitrogen: int
    phosphorus: int
    potassium: int
    light_raw: int
    light_percent: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SoilDataResponse(SoilData):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


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
