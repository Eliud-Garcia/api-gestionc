from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME:str = "API Mi Vehiculo"
    PROJECT_VERSION:str = "1.0.0"
    PROJECT_DESCRIPTION:str = "API para la gestión de vehiculos"
    DATABASE_URL:str
    FUSEKI_ENDPOINT_URL:str
    SECRET_KEY: str = "supersecretkey_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
