from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import factura, servicio, tarjeta_propiedad, usuario, vehiculo, semantic
from src.api.routes import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

#incluir las rutas
app.include_router(auth.router, prefix='/api/auth', tags=['Autenticación'])
app.include_router(usuario.router, prefix='/api/usuarios', tags=['Usuarios'])
app.include_router(semantic.router, prefix='/api/semantica', tags=['Ontología Semántica'])
app.include_router(factura.router, prefix='/api/facturas', tags=['Facturas'])


# para iniciar el servidor
# uvicorn src.main:app --reload

# para hacer migraciones
# alembic revision --autogenerate -m 'mesaje migracion'

# para aplicar las migraciones
# alembic upgrade head

# para revertir las migraciones
# alembic downgrade -1