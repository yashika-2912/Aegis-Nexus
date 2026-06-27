from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Aegis Nexus Phase 1"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None


settings = Settings()
