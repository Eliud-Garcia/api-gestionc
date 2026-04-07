from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME:str = "API Mi Vehiculo"
    PROJECT_VERSION:str = "1.0.0"
    PROJECT_DESCRIPTION:str = "API para la gestión de vehiculos"
    DATABASE_URL:str
    FUSEKI_ENDPOINT_URL:str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GROQ_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str

    class Config:
        env_file = ".env"

settings = Settings()
