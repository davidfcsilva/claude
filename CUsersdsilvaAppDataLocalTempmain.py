"""Demo backend using FastAPI."""

import os

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="ArgoCD Demo Backend", version="0.1.0")

_APP_MODULE_PATH = "/app/main.py"


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


_ITEMS = [
    {"id": 1, "name": "Widget A"},
    {"id": 2, "name": "Widget B"},
    {"id": 3, "name": "Widget C"},
    {"id": 4, "name": "Widget D"},
    {"id": 5, "name": "Widget E"},
]


@app.get("/api/items")
async def get_items(response: Response) -> list[dict]:
    """Return a demo list of items."""
    response.headers["Cache-Control"] = "max-age=60, stale-while-revalidate=30"
    return _ITEMS


@app.get("/")
async def root() -> dict:
    """Root endpoint — simple greeting."""
    return {"message": "Hello from the ArgoCD demo backend!"}

@app.post("/reload")
async def reload_from_disk() -> dict:
    """Hot-reload app state from its ConfigMap volume mount.

    Reads /app/main.py from disk (mounted by ArgoCD), exec's the
    file against this module's globals, and updates any dynamic
    variables (e.g. _ITEMS) without a pod restart.
    """
    path = _APP_MODULE_PATH
    if not os.path.isfile(path):
        return {"ok": False, "error": f"file not found: {path}"}

    with open(path, "r") as f:
        source = f.read()

    ctx = {"_ITEMS": _ITEMS, "app": app, "__name__": "__main__", "__builtins__": __builtins__}
    exec(source, ctx)  # noqa: S102  # safe — we control the mounted file

    if "_ITEMS" in ctx:
        _ITEMS.clear()
        _ITEMS.extend(ctx["_ITEMS"])

    return {"ok": True, "path": path, "loaded_items": len(_ITEMS)}
