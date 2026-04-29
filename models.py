from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
<<<<<<< HEAD
from app.database import Base
=======
from database import Base
>>>>>>> e383d38da4b7ada234135755e995e610e46f44f9
class EstacionDB(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    ubicacion = Column(String)
    # Relación: permite acceder a las lecturas desde el objeto estación
    lecturas = relationship("LecturaDB", back_populates="estacion")
class LecturaDB(Base):
    __tablename__ = "lecturas"
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float)
    estacion_id = Column(Integer, ForeignKey("estaciones.id"))
    estacion = relationship("EstacionDB", back_populates="lecturas")