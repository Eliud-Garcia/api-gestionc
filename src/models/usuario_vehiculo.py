from sqlalchemy import Column, Integer, BigInteger, Date, String, ForeignKey
from src.db.base_class import Base

class UsuarioVehiculo(Base):
    __tablename__ = "usuario_vehiculo"
    pfk_usuario = Column(BigInteger, ForeignKey("usuario.documento_identidad"),primary_key=True)
    pfk_vehiculo = Column(String(6), ForeignKey("vehiculo.placa"),primary_key=True)
    fecha_registro = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)
    kilometros_registro = Column(Integer, nullable=False)