"""
Entry point shim -- re-exports the FastAPI app from the backend package.
This keeps backward compatibility with the existing Dockerfile CMD.
"""

from backend.main import app  # noqa: F401
