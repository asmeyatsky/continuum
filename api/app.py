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
        """Initialize the engine when the application starts."""
        import logging
        from core.concept_orchestrator import DefaultConceptOrchestrator
        from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
        from feedback_system.core import SelfImprovingFeedbackSystem
        from content_generation.multimodal import MockMultimodalContentGenerator
        from data_pipeline.ingestion import MockDataIngestionPipeline
        from llm_service.factory import get_llm_service
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        
        if not engine:  # Only initialize if not provided
            try:
                # Initialize the core components
                llm_service = get_llm_service()
                logger.info("LLM service initialized")
                
                ingestion_pipeline = MockDataIngestionPipeline()
                logger.info("Data ingestion pipeline initialized")
                
                knowledge_graph = InMemoryKnowledgeGraphEngine()
                logger.info("Knowledge graph engine initialized")
                
                feedback_system = SelfImprovingFeedbackSystem()
                logger.info("Feedback system initialized")
                
                content_generator = MockMultimodalContentGenerator()
                logger.info("Content generator initialized")
                
                orchestrator = DefaultConceptOrchestrator()  # Using the concrete implementation
                logger.info("Concept orchestrator initialized")
                
                # Set the engine for the routes
                set_engine(orchestrator)
                logger.info("Engine set for API routes")
                
            except Exception as e:
                logger.error(f"Error initializing engine: {e}")
                import traceback
                traceback.print_exc()
                raise

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

    # Create the app without engine (it will be set during startup)
    app = create_app()
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
    )
