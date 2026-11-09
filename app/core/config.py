from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación cargada desde entorno o .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # La URL de conexión se lee del entorno (.env o variables del proceso).
    # Sin valor por defecto con credenciales: si falta DATABASE_URL, la
    # instanciación de Settings falla de manera controlada y la app no arranca.
    DATABASE_URL: str
    SQL_ECHO: bool = False
    PORT: int = 8000

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalizar_database_url(cls, v: str) -> str:
        """Asegura que el esquema de conexión use el driver asyncpg."""
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """Retorna una instancia cacheada de la configuración."""
    return Settings()
