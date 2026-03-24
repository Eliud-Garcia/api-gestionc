from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import factura, servicio, tarjeta_propiedad, usuario, vehiculo

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

#incluir las rutas
app.include_router(usuario.router, prefix='/usuarios', tags=['Usuarios'])



# para iniciar el servidor
# uvicorn src.main:app --reload

# para hacer migraciones
# alembic revision --autogenerate -m 'mesaje migracion'

# para aplicar las migraciones
# alembic upgrade head

# para revertir las migraciones
# alembic downgrade -1