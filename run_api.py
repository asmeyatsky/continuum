#!/usr/bin/env python3
"""
Script to run the API server with proper engine initialization.
"""
import traceback
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.app import create_app
    from core.concept_orchestrator import DefaultConceptOrchestrator  # Using the default implementation
    from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
    from feedback_system.core import SelfImprovingFeedbackSystem
    from content_generation.multimodal import MockMultimodalContentGenerator
    from data_pipeline.ingestion import MockDataIngestionPipeline
    from llm_service.factory import get_llm_service
    import uvicorn
    
    print("Initializing LLM service...")
    llm_service = get_llm_service()
    print("LLM service initialized!")
    
    print("Initializing data ingestion pipeline...")
    ingestion_pipeline = MockDataIngestionPipeline()
    print("Data ingestion pipeline initialized!")
    
    print("Initializing knowledge graph engine...")
    knowledge_graph = InMemoryKnowledgeGraphEngine()
    print("Knowledge graph engine initialized!")
    
    print("Initializing feedback system...")
    feedback_system = SelfImprovingFeedbackSystem()
    print("Feedback system initialized!")
    
    print("Initializing content generator...")
    content_generator = MockMultimodalContentGenerator()
    print("Content generator initialized!")
    
    print("Initializing concept orchestrator...")
    orchestrator = DefaultConceptOrchestrator()  # Using the actual implementation
    print("Concept orchestrator initialized!")
    
    print("Creating application with initialized engine...")
    app = create_app(engine=orchestrator)
    print("Application created successfully with initialized engine!")
    
    print("Starting server on http://0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except Exception as e:
    print(f"Error starting server: {e}")
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)