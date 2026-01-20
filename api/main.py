"""
Entry point for the FastAPI application.
Exposes the 'app' object for Uvicorn to run.
"""
from api.app import create_app

app = create_app()
