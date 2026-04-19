"""FastAPI application entrypoint for Babylon backend services."""

from fastapi import FastAPI

app = FastAPI(title="Babylon API")


@app.get("/")
async def root() -> dict[str, str]:
    """Return a basic service status payload."""
    return {"status": "ok", "message": "Babylon API is online"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return a lightweight healthcheck response for orchestrators."""
    # This is useful for Docker healthchecks later
    return {"status": "healthy"}
