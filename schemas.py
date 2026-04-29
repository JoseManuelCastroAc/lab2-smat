from pydantic import BaseModel, ConfigDict

class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str
    model_config = ConfigDict(from_attributes=True)

class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float
    model_config = ConfigDict(from_attributes=True)

# Representa las lecturas y estaciones ya existentes
class LecturaDB(BaseModel):
    id: int
    valor: float
    estacion_id: int
    model_config = ConfigDict(from_attributes=True)


class EstacionDB(BaseModel):
    id: int
    nombre: str
    ubicacion: str

    model_config = ConfigDict(from_attributes=True)