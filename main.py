import asyncpg
import os

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Conexión a la base de datos PostgreSQL
async def connect_to_postgres():
    DATABASE_URL = os.environ['DATABASE_URL']
    return await asyncpg.connect(DATABASE_URL)

# Modelos de datos
class Deporte(BaseModel):
    nombre: str

# Operaciones CRUD para Deportes
@app.post("/deportes/", response_model=Deporte)
async def crear_deporte(deporte: Deporte, conn = Depends(connect_to_postgres)):
    deporte_id = await conn.fetchval("INSERT INTO deportes (nombre) VALUES ($1) RETURNING id", deporte.nombre)
    return {"id": deporte_id, "nombre": deporte.nombre}

@app.get("/deportes/", response_model=List[Deporte])
async def listar_deportes(conn = Depends(connect_to_postgres)):
    deportes = await conn.fetch("SELECT * FROM deportes")
    return [{"id": deporte['id'], "nombre": deporte['nombre']} for deporte in deportes]

@app.put("/deportes/{deporte_id}/", response_model=Deporte)
async def actualizar_deporte(deporte_id: int, deporte: Deporte, conn = Depends(connect_to_postgres)):
    await conn.execute("UPDATE deportes SET nombre = $1 WHERE id = $2", deporte.nombre, deporte_id)
    return {"id": deporte_id, "nombre": deporte.nombre}

@app.delete("/deportes/{deporte_id}/", response_model=Deporte)
async def eliminar_deporte(deporte_id: int, conn = Depends(connect_to_postgres)):
    deporte = await conn.fetchrow("SELECT nombre FROM deportes WHERE id = $1", deporte_id)
    if not deporte:
        raise HTTPException(status_code=404, detail="Deporte no encontrado")
    await conn.execute("DELETE FROM deportes WHERE id = $1", deporte_id)
    return {"id": deporte_id, "nombre": deporte['nombre']}
