"""
FastAPI application factory for the Continuum API.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router, set_engine
from config.settings import settings
from config.logging_config import setup_logging

logger = logging.getLogger(__name__)


def create_app(engine=None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        engine: Optional Continuum engine instance

    Returns:
        FastAPI application instance
    """
    # Setup logging
    setup_logging(
        level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE,
        name="continuum",
    )

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Infinite Concept Expansion Engine with knowledge graphs and autonomous research",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on environment in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router)

    # Set engine for routes
    if engine:
        set_engine(engine)
        logger.info("Engine set for API routes")

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {settings.APP_NAME}")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
    )
