"""
Main entry point for the Enhanced Infinite Concept Expansion Engine.

This module orchestrates the entire system, connecting all components to
provide autonomous concept expansion capabilities with advanced visualization
and persistent learning that improves over time.
"""
from core.concept_orchestrator import DefaultConceptOrchestrator
from agents.base import AgentManager
from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
from data_pipeline.ingestion import MockDataIngestionPipeline
from content_generation.multimodal import MockMultimodalContentGenerator
from feedback_system.core import SelfImprovingFeedbackSystem
from utils.visualization import AdvancedKnowledgeGraphVisualizer, PersistentLearningSystem, RealTimeEvolutionMonitor
from datetime import datetime
import asyncio
import uuid


class EnhancedInfiniteConceptExpansionEngine:
    """
    The enhanced main class for the Infinite Concept Expansion Engine.
    
    This orchestrates all components to provide autonomous concept expansion capabilities
    with advanced visualization, persistent learning, and continuous improvement.
    """
    
    def __init__(self):
        self.orchestrator = DefaultConceptOrchestrator()
        self.agent_manager = AgentManager()
        self.knowledge_graph = InMemoryKnowledgeGraphEngine()
        self.data_pipeline = MockDataIngestionPipeline()
        self.content_generator = MockMultimodalContentGenerator()
        self.feedback_system = SelfImprovingFeedbackSystem()
        
        # Enhanced components
        self.visualizer = AdvancedKnowledgeGraphVisualizer(self.knowledge_graph)
        self.persistent_learner = PersistentLearningSystem(self.knowledge_graph, self.feedback_system)
        self.evolution_monitor = RealTimeEvolutionMonitor(self.knowledge_graph, self.persistent_learner)
        
        # Register components for cross-communication
        self._setup_component_communication()
    
    def _setup_component_communication(self):
        """Setup communication between components"""
        # In a real system, this would register callbacks or message queues
        pass
    
    def submit_concept(self, concept: str) -> str:
        """Submit a concept for expansion and return exploration ID"""
        exploration_id = self.orchestrator.submit_exploration_request(concept)
        print(f"🚀 Started exploration for concept '{concept}' with ID: {exploration_id}")
        
        # Record in persistent learning system
        self.persistent_learner.record_learning_event(
            event_type="exploration_started",
            data={
                "concept": concept,
                "exploration_id": exploration_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return exploration_id
    
    async def run_single_expansion_cycle(self, exploration_id: str):
        """Run a single expansion cycle for an exploration"""
        # Get the next task from the orchestrator
        task = self.orchestrator.get_next_task()
        if not task:
            print(f"⏳ No tasks available for exploration {exploration_id}")
            return
        
        print(f"⚙️  Processing task: {task.concept} (Type: {task.task_type})")
        
        # Execute the task with relevant agents
        agent_responses = self.agent_manager.execute_task(task)
        
        # Process each response
        for response in agent_responses:
            print(f"🤖 Agent {response.agent_name} completed with success: {response.success}")
            
            if response.success:
                # Convert agent response to concept node and add to knowledge graph
                node_id = str(uuid.uuid4())
                concept_node = self._create_concept_node(
                    node_id, 
                    task.concept, 
                    str(response.data), 
                    response.agent_name,
                    response.metadata
                )
                
                # Add to knowledge graph
                self.knowledge_graph.add_node(concept_node)
                
                # Add edges to connect to parent concept if applicable
                if hasattr(task, 'parent_node_id') and task.parent_node_id:
                    from knowledge_graph.engine import GraphEdge
                    edge = GraphEdge(
                        id=str(uuid.uuid4()),
                        source_node_id=task.parent_node_id,
                        target_node_id=node_id,
                        relationship_type="expands_to",
                        weight=response.confidence,
                        created_at=datetime.now(),
                        metadata={"agent": response.agent_name}
                    )
                    self.knowledge_graph.add_edge(edge)
                
                # Add to orchestrator's tracking
                self.orchestrator.add_concept_node(concept_node)
                
                # Record learning event for persistent improvement
                self.persistent_learner.record_learning_event(
                    event_type="node_created",
                    data={
                        "node_id": node_id,
                        "concept": concept_node.concept,
                        "source_agent": response.agent_name,
                        "confidence": response.confidence,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        # Record performance in feedback system
        success_count = sum(1 for resp in agent_responses if resp.success)
        avg_confidence = sum(resp.confidence for resp in agent_responses) / len(agent_responses) if agent_responses else 0.0
        
        self.feedback_system.record_system_feedback(
            feedback_type="expansion_success",
            item_id=task.id,
            rating=min(1.0, avg_confidence),  # Use average confidence as rating
            metadata={
                "exploration_id": exploration_id,
                "task_type": task.task_type,
                "agent_count": len(agent_responses),
                "successful_agents": success_count,
                "avg_confidence": avg_confidence,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _create_concept_node(self, node_id: str, concept: str, content: str, 
                           source_agent: str, metadata: dict):
        """Create a concept node from agent response"""
        from core.concept_orchestrator import ConceptNode
        
        return ConceptNode(
            id=node_id,
            concept=concept,
            content=content,
            metadata={
                "source_agent": source_agent,
                "original_task_id": metadata.get("task_id"),
                "created_at": datetime.now().isoformat(),
                "enhanced": True,  # Mark as enhanced node
                **metadata
            },
            created_at=datetime.now(),
            connections=[]
        )
    
    async def expand_concept(self, concept: str, max_expansions: int = 5):
        """Run a complete expansion process for a concept"""
        print(f"🔬 Starting expansion for concept: {concept}")
        
        # Submit the concept
        exploration_id = self.submit_concept(concept)
        
        # Run multiple expansion cycles
        for i in range(max_expansions):
            print(f"\n--- 🌀 Expansion Cycle {i+1} ---")
            await self.run_single_expansion_cycle(exploration_id)
            
            # Small delay between cycles to simulate processing time
            await asyncio.sleep(0.5)
        
        # Generate content for the discovered concepts
        print("\n--- 🎨 Generating Multimodal Content ---")
        await self._generate_multimodal_content(exploration_id)
        
        # Create visualization
        print("\n--- 📊 Creating Visualizations ---")
        await self._create_visualizations(exploration_id)
        
        # Print detailed summary
        self._print_expansion_summary(exploration_id)
        
        # Generate evolution insights
        self._generate_evolution_insights()
        
        return exploration_id
    
    async def _generate_multimodal_content(self, exploration_id: str):
        """Generate multimodal content for discovered concepts"""
        # Get concepts from the knowledge graph
        all_concepts = [node.concept for node in self.knowledge_graph.nodes.values()][:4]  # Get first 4 concepts
        
        if not all_concepts:
            # If no concepts in graph, use sample concepts
            all_concepts = ["AI Research", "Machine Learning", "Neural Networks", "Data Science"]
        
        for concept in all_concepts:
            print(f"🎨 Generating multimodal content for: {concept}")
            
            # Generate multimodal package
            multimodal_package = self.content_generator.generate_multimodal_package(concept)
            
            # Validate content quality
            from content_generation.multimodal import ContentQualityValidator
            validator = ContentQualityValidator()
            
            for content_type, content in multimodal_package.items():
                validation = validator.validate_content(content)
                print(f"  {content_type}: Quality Score = {validation['quality_score']:.2f}")
                
                # Record quality in feedback system
                self.feedback_system.record_system_feedback(
                    feedback_type="content_quality",
                    item_id=content.id,
                    rating=validation['quality_score'],
                    metadata={
                        "content_type": content_type,
                        "exploration_id": exploration_id,
                        "validation_issues": validation.get('issues', []),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Record in persistent learning system
                self.persistent_learner.record_learning_event(
                    event_type="content_quality_feedback",
                    data={
                        "concept": concept,
                        "content_type": content_type,
                        "quality_score": validation['quality_score'],
                        "validation_issues": validation.get('issues', []),
                        "timestamp": datetime.now().isoformat()
                    }
                )
    
    async def _create_visualizations(self, exploration_id: str):
        """Create and save visualizations for the exploration"""
        try:
            # Create 3D knowledge graph
            print("   📈 Creating 3D knowledge graph...")
            graph_fig = self.visualizer.create_3d_knowledge_graph(exploration_id)
            self.visualizer.save_visualization(graph_fig, f"knowledge_graph_{exploration_id}", "html")
            
            # Create dashboard
            print("   📊 Creating comprehensive dashboard...")
            dashboard_fig = self.visualizer.create_dashboard(exploration_id)
            self.visualizer.save_visualization(dashboard_fig, f"dashboard_{exploration_id}", "html")
            
            # Create evolution timeline
            print("   📅 Creating evolution timeline...")
            timeline_fig = self.visualizer.create_evolution_timeline([])
            self.visualizer.save_visualization(timeline_fig, f"timeline_{exploration_id}", "html")
            
            print(f"   ✅ Visualizations saved for exploration {exploration_id}")
        except Exception as e:
            print(f"   ⚠️  Error creating visualizations: {e}")
    
    def _print_expansion_summary(self, exploration_id: str):
        """Print a detailed summary of the expansion"""
        print(f"\n--- 📋 Expansion Summary for ID: {exploration_id} ---")
        print(f"📊 Knowledge Graph Nodes: {self.knowledge_graph.get_node_count()}")
        print(f"🔗 Knowledge Graph Edges: {self.knowledge_graph.get_edge_count()}")
        
        # Show feedback summary
        improvement_recommendations = self.feedback_system.get_improvement_recommendations()
        if improvement_recommendations:
            print(f"💡 Improvement Recommendations: {len(improvement_recommendations)}")
            for rec in improvement_recommendations[:3]:  # Show first 3
                print(f"   • {rec['recommendation']} (Priority: {rec['priority']})")
        else:
            print("✅ No improvement recommendations at this time")
        
        # Show persistent learning insights
        persistent_recommendations = self.persistent_learner.get_improvement_recommendations()
        if persistent_recommendations:
            print(f"🧠 Persistent Learning Insights: {len(persistent_recommendations)}")
            for rec in persistent_recommendations[:2]:  # Show first 2
                print(f"   • {rec['recommendation']}")
        
        # Show pattern analysis
        pattern_analysis = self.feedback_system.analyze_expansion_patterns()
        print(f"🔍 Expansion Pattern Analysis:")
        for key, value in list(pattern_analysis.items())[:3]:  # Show first 3 keys
            print(f"   • {key}: {str(value)[:100]}...")  # Truncate long values
    
    def _generate_evolution_insights(self):
        """Generate insights about system evolution"""
        print(f"\n--- 🧬 System Evolution Insights ---")
        insights = self.evolution_monitor.generate_insights()
        
        for insight in insights[-3:]:  # Show last 3 insights
            emoji = "🟢" if insight["priority"] == "low" else "🟡" if insight["priority"] == "medium" else "🔴"
            print(f"   {emoji} {insight['title']}")
            print(f"      {insight['description']}")
        
        # Show evolution report
        report = self.evolution_monitor.get_evolution_report()
        print(f"\n📈 System Health: {report['system_health']}")
        print(f"   Total Learning Events: {report['current_metrics']['learning_events_today']}")
        print(f"   Connection Density: {report['current_metrics']['connection_density']:.2f}")
        print(f"   Concept Diversity: {report['current_metrics']['diversity_score']:.2f}")
    
    def get_discovered_concepts(self, exploration_id: str) -> list:
        """Get all discovered concepts from the knowledge graph"""
        concepts = [node.concept for node in self.knowledge_graph.nodes.values()]
        return concepts[:10]  # Return up to 10 concepts
    
    def continuous_learning_mode(self):
        """Enter continuous learning mode that improves over time"""
        print("\n🔄 Entering Continuous Learning Mode...")
        print("The system will continuously expand knowledge and improve its capabilities over time.")
        print("The longer it runs, the better it gets!")
        
        async def learning_cycle():
            concepts_to_explore = [
                "Artificial Intelligence", "Machine Learning", "Quantum Computing", 
                "Biotechnology", "Renewable Energy", "Space Exploration"
            ]
            
            cycle_count = 0
            while True:
                try:
                    concept = concepts_to_explore[cycle_count % len(concepts_to_explore)]
                    print(f"\n--- 🔄 Continuous Learning Cycle {cycle_count + 1} ---")
                    
                    # Run a quick expansion
                    exploration_id = await self.expand_concept(concept, max_expansions=2)
                    
                    # Wait before next cycle
                    await asyncio.sleep(5)  # Wait 5 seconds between cycles
                    
                    # Every 5 cycles, generate a comprehensive report
                    if (cycle_count + 1) % 5 == 0:
                        print(f"\n📈 GENERATING COMPREHENSIVE REPORT - Cycle {cycle_count + 1}")
                        evolution_report = self.evolution_monitor.get_evolution_report()
                        print(f"System Health: {evolution_report['system_health']}")
                        print(f"Total Nodes: {evolution_report['current_metrics']['node_count']}")
                        print(f"Learning Events Today: {evolution_report['current_metrics']['learning_events_today']}")
                    
                    cycle_count += 1
                    
                except KeyboardInterrupt:
                    print("\n🛑 Continuous learning mode interrupted by user")
                    break
                except Exception as e:
                    print(f"Error in learning cycle: {e}")
                    await asyncio.sleep(10)  # Wait longer if there's an error
        
        return learning_cycle()


async def main():
    """Main function to demonstrate the Enhanced Infinite Concept Expansion Engine"""
    print("🚀🌟 ENHANCED Infinite Concept Expansion Engine 🌟🚀")
    print("  The longer it runs, the better it gets!")
    print("="*70)
    
    # Initialize the enhanced engine
    engine = EnhancedInfiniteConceptExpansionEngine()
    
    # Example exploration
    concept_to_expand = "Artificial Intelligence"
    print(f"🔬 Exploring concept: {concept_to_expand}")
    
    # Run the expansion
    exploration_id = await engine.expand_concept(concept_to_expand, max_expansions=3)
    
    print("\n" + "="*70)
    print("✅ Expansion completed!")
    print(f"Explorer ID: {exploration_id}")
    
    # Get discovered concepts
    discovered = engine.get_discovered_concepts(exploration_id)
    print(f"\n🧠 Discovered {len(discovered)} related concepts:")
    for i, concept in enumerate(discovered, 1):
        print(f"  {i}. {concept}")
    
    # Show evolution insights
    print(f"\n🔄 System Evolution Status:")
    report = engine.evolution_monitor.get_evolution_report()
    print(f"   • System Health: {report['system_health']}")
    print(f"   • Knowledge Nodes: {report['current_metrics']['node_count']}")
    print(f"   • Connection Density: {report['current_metrics']['connection_density']:.2f}")
    print(f"   • Learning Events: {report['current_metrics']['learning_events_today']}")
    
    # Ask user if they want to enter continuous learning mode
    print(f"\n🎯 Would you like to enter CONTINUOUS LEARNING MODE?")
    print("   This mode runs indefinitely, improving the system over time.")
    print("   (Press Ctrl+C to exit continuous mode)")
    
    response = input("   Enter 'yes' to start continuous learning, or any other key to exit: ").strip().lower()
    
    if response == 'yes':
        print("\n🌟 Starting Continuous Learning Mode...")
        print("   This mode will run indefinitely and improve over time!")
        print("   Press Ctrl+C at any time to stop.")
        await engine.continuous_learning_mode()
    else:
        print(f"\n✨ Enhanced Infinite Concept Expansion Engine session completed!")
        print(f"   Visualizations have been saved to the project directory")
        print(f"   Check knowledge_graph_{exploration_id}.html and dashboard_{exploration_id}.html files")


if __name__ == "__main__":
    asyncio.run(main())