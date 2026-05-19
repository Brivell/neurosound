from fastapi import Request
from database.engine import get_db  # noqa: re-exported for convenience

__all__ = ["get_db"]


def get_registry(request: Request) -> dict:
    """Return the global model registry stored in app state."""
    return getattr(request.app.state, "registry", {})
