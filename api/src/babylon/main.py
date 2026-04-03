# src/babylon/main.py
from fastapi import FastAPI

app = FastAPI(title="Babylon API")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "Babylon API is online"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    # This is useful for Docker healthchecks later
    return {"status": "healthy"}
