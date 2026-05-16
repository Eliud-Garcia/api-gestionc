from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.routes import factura, usuario, semantic, ia
from src.api.routes import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #dominio de la web que va a consumir la api
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#incluir las rutas
app.include_router(auth.router, prefix='/api/auth', tags=['Autenticación'])
app.include_router(usuario.router, prefix='/api/usuarios', tags=['Usuarios'])
app.include_router(factura.router, prefix='/api/facturas', tags=['Facturas'])
app.include_router(ia.router, prefix='/api/ia', tags=['Inteligencia Artificial'])
app.include_router(semantic.router, prefix='/api/semantica', tags=['Ontología Semántica'])


# para iniciar el servidor
# uvicorn src.main:app --reload
