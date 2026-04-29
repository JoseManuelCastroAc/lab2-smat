from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

import app.models as models
import app.schemas as schemas

def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    nueva_estacion = models.EstacionDB(
        id=estacion.id,
        nombre=estacion.nombre,
        ubicacion=estacion.ubicacion
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion


def obtener_estaciones(db: Session):
    return db.query(models.EstacionDB).all()


def obtener_estacion(db: Session, id: int):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no registrada")
    return estacion


def crear_lectura(db: Session, lectura: schemas.LecturaCreate):
    estacion = db.query(models.EstacionDB).filter(
        models.EstacionDB.id == lectura.estacion_id
    ).first()

    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")

    nueva_lectura = models.LecturaDB(
        valor=lectura.valor,
        estacion_id=lectura.estacion_id
    )

    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)

    return nueva_lectura


def obtener_historial(db: Session, id: int):
    estacion = obtener_estacion(db, id)

    lecturas = db.query(models.LecturaDB).filter(
        models.LecturaDB.estacion_id == id
    ).all()

    conteo = len(lecturas)
    promedio = 0.0

    if conteo > 0:
        promedio = sum(l.valor for l in lecturas) / conteo

    return {
        "estacion_id": id,
        "nombre_estacion": estacion.nombre,
        "conteo": conteo,
        "promedio": promedio,
        "lecturas": lecturas
    }


def obtener_criticos(db: Session, umbral: float):
    lecturas = db.query(models.LecturaDB).filter(
        models.LecturaDB.valor >= umbral
    ).all()

    return {
        "umbral_aplicado": umbral,
        "total_criticos": len(lecturas),
        "registros": lecturas
    }


def obtener_stats(db: Session):
    lectura_maxima = db.query(models.LecturaDB).order_by(models.LecturaDB.valor.desc()).first()
    
    if lectura_maxima is None:
        estacion_nombre = "N/A"
        valor_max = 0.0
    else:
        valor_max = lectura_maxima.valor
        # Buscamos el nombre de la estación en relacion
        estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura_maxima.estacion_id).first()
        estacion_nombre = estacion.nombre if estacion else "Desconocida"

    return {
        "entidad": "FACULTAD DE INGENIERÍA DE SISTEMAS E INFORMATICA - UNMSM",
        "proyecto": "SMAT - Monitoreo Ambiental",
        "estadisticas_globales": {
            "total_estaciones_monitoreo": db.query(models.EstacionDB).count(),
            "total_muestras_telemetria": db.query(models.LecturaDB).count(),
            "punto_critico_maximo": {
                "estacion": estacion_nombre,
                "valor": valor_max
            }
        }
    }


def obtener_riesgo(db: Session, id: int):
    estacion = obtener_estacion(db, id)

    ultima = db.query(models.LecturaDB).filter(
        models.LecturaDB.estacion_id == id
    ).order_by(models.LecturaDB.id.desc()).first()

    if not ultima:
        return {"estacion": estacion.nombre, "riesgo": "SIN DATOS"}

    if ultima.valor > 80:
        nivel = "PELIGRO"
    elif ultima.valor > 50:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"

    return {
        "estacion_id": id,
        "nombre": estacion.nombre,
        "nivel_riesgo": nivel
    }