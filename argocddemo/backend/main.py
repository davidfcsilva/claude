"""Demo backend using FastAPI."""

from fastapi import FastAPI

app = FastAPI(title="ArgoCD Demo Backend", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/items")
async def get_items() -> list[dict]:
    """Return a demo list of items."""
    return [
        {"id": 1, "name": "Widget A"},
        {"id": 2, "name": "Widget B"},
        {"id": 3, "name": "Widget C"},
    ]


@app.get("/")
async def root() -> dict:
    """Root endpoint — simple greeting."""
    return {"message": "Hello from the ArgoCD demo backend!"}
