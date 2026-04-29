from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import app.models as models
import app.crud as crud
import app.schemas as schemas
from app.database import engine, get_db
from app.schemas import EstacionCreate, LecturaCreate, LecturaDB
from app.auth import crear_token_acceso, obtener_identidad_actual

# ==========================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# Esta línea busca el archivo 'smat.db' y crea las tablas
# definidas en models.py si es que aún no existen.
# ==========================================================
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
API robusta para la gestión y monitoreo de desastres naturales.
Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.

**Entidades principales:**
* **Estaciones:** Puntos de monitoreo físico.
* **Lecturas:** Datos capturados por sensores.
* **Riesgos:** Análisis de criticidad basado en umbrales.
""",
    version="1.0.0",
    terms_of_service="http://unmsm.edu.pe/terms/",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "url": "http://fisi.unmsm.edu.pe",
        "email": "desarrollo.smat@unmsm.edu.pe",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = ["*"] # En producción, especificar dominios reales
app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

@app.post(
    "/estaciones/",
    status_code=201,
    tags=["Gestión de Infraestructura"],
    summary="Registrar una nueva estación de monitoreo",
    description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    return {
        "msj": "Estación guardada en DB",
        "data": crud.crear_estacion(db, estacion)
    }


@app.post(
    "/lecturas/",
    status_code=201,
    tags=["Telemetría de Sensores"],
    summary="Recibir datos de telemetría",
    description="Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante su ID."
)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db), usuario: str = Depends(obtener_identidad_actual)):
    estacion_db = db.query(models.EstacionDB).filter(
        models.EstacionDB.id == lectura.estacion_id
    ).first()

    if not estacion_db:
        raise HTTPException(
            status_code=404,
            detail="Error de Integridad: La estación no existe en la base de datos."
        )

    crud.crear_lectura(db, lectura)

    return {"status": "Lectura guardada en DB"}



@app.get(
    "/estaciones/{id}/historial",
    tags=["Reportes Históricos"],
    summary="Obtener historial de lecturas y estadísticas",
    description="""
    Se valida la existencia de la DB de estaciones, debido a que luego lo usaremos
    Los calculos estadisticos usados son: Conteo y promedio. Los que serán retornados junto a estacion_id, nombre_estacion y lecturas del id solicitado
    """
)
def obtener_historial(id: int, db: Session = Depends(get_db)):
    return crud.obtener_historial(db, id)


@app.get(
    "/reportes/criticos",
    tags=["Auditoría"],
    summary="Identificar lecturas que superan el umbral",
    description="""
    Se realiza un filtro inicial donde se capturas las lecturas de la DB donde el umbral de valor sea mayor o igual añ umbral solicitado (El default sera 80)
    Luego del filtro se retorna el json con los siguientes 3 campos: Umbral_aplicado, total_criticos y registros.
    """
)
def obtener_reportes_criticos(
    umbral: float = Query(80.0, description="Valor filtro para lecturas críticas"),
    db: Session = Depends(get_db)
):
    return crud.obtener_criticos(db, umbral)


@app.get(
    "/estaciones/stats",
    tags=["Resumen Ejecutivo"],
    summary="Resumen ejecutivo del sistema",
    description="""
    Endpoint que entrega un resumen tanto de lecturas como de estaciones existentes y registradas en la DB
    """
)
def obtener_stats_ejecutivas(db: Session = Depends(get_db)):
    return crud.obtener_stats(db)


@app.get(
    "/estaciones/{id}/riesgo",
    tags=["Análisis de Riesgo"],
    summary="Evaluar nivel de peligro actual",
    description="Encuentra la última lectura recibida de una estación con filtro determina si es: NORMAL, ALERTA o PELIGRO."
)
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    return crud.obtener_riesgo(db, id)


@app.get(
    "/estaciones/",
    response_model=List[EstacionCreate],
    tags=["Gestión de Infraestructura"],
    summary="Listar todas las estaciones",
    description="Retorna el catálogo completo de estaciones registradas en el sistema."
)
def retornar_estaciones(db: Session = Depends(get_db)):
    return crud.obtener_estaciones(db)

# Endpoint para obtener el Token (Simulación de Login)
@app.post("/token", tags=["Seguridad"])
async def login_para_obtener_token():
    # En la Unidad II esto validará contra la tabla de usuarios
    return {"access_token": crear_token_acceso({"sub": "admin_smat"}), "token_type": "bearer"}
# Endpoint Protegido: Solo accesible con Token válido
@app.post("/estaciones/", status_code=201, tags=["Infraestructura"])
def crear_estacion(
    estacion: schemas.EstacionCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual) # PROTECCIÓN JWT
    ):
    return crud.crear_estacion(db=db, estacion=estacion)