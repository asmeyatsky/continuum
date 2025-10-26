"""
Enhanced Visualization Engine for the Infinite Concept Expansion Engine.

This module provides advanced visualization capabilities including 3D knowledge graphs,
interactive dashboards, and real-time evolution tracking.
"""
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import uuid
from knowledge_graph.engine import InMemoryKnowledgeGraphEngine, ConceptNode, GraphEdge
import json
import os


class AdvancedKnowledgeGraphVisualizer:
    """Advanced visualizer for the knowledge graph with multiple visualization modes"""
    
    def __init__(self, knowledge_graph: InMemoryKnowledgeGraphEngine):
        self.knowledge_graph = knowledge_graph
        self.visualization_cache = {}
    
    def create_3d_knowledge_graph(self, exploration_id: str = "current", title: str = "Knowledge Graph Visualization") -> go.Figure:
        """Create an interactive 3D visualization of the knowledge graph"""
        # Get nodes and edges from the knowledge graph
        nodes = list(self.knowledge_graph.nodes.values())
        
        if not nodes:
            # If no nodes exist, create a sample graph
            nodes = self._create_sample_nodes()
        
        # Generate 3D coordinates for nodes
        n = len(nodes)
        if n == 0:
            # Create a minimal sample
            nodes = [ConceptNode(
                id="sample1",
                concept="Sample Concept",
                content="Sample content for visualization",
                metadata={},
                created_at=datetime.now(),
                connections=[]
            )]
            n = 1
        
        # Generate 3D coordinates
        theta = np.linspace(0, 2 * np.pi, n)
        r = np.linspace(0.5, 2, n)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.sin(theta) * np.linspace(0, 1, n)  # Create a spiral effect in 3D
        
        # Create edge connections (simplified - connect each node to the next)
        edges_x = []
        edges_y = []
        edges_z = []
        
        for i, node in enumerate(nodes):
            # Connect to neighbors in the sequence
            if i < len(nodes) - 1:
                edges_x.extend([x[i], x[i+1], None])
                edges_y.extend([y[i], y[i+1], None])
                edges_z.extend([z[i], z[i+1], None])
        
        # Create the 3D plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter3d(
            x=edges_x, y=edges_y, z=edges_z,
            mode='lines',
            line=dict(color='lightgray', width=2),
            hoverinfo='none',
            name='Connections'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+text',
            marker=dict(
                size=8,
                color=np.arange(len(nodes)),  # Color based on position
                colorscale='Viridis',
                colorbar=dict(title="Node Index"),
                line=dict(width=2, color='black')
            ),
            text=[node.concept[:20] + "..." if len(node.concept) > 20 else node.concept for node in nodes],
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>Content: %{customdata}<extra></extra>',
            customdata=[node.content[:50] + "..." if len(node.content) > 50 else node.content for node in nodes],
            name='Concepts'
        ))
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                bgcolor='rgba(0,0,0,0.05)'
            ),
            showlegend=True,
            height=800,
            width=1000,
            template='plotly_dark'
        )
        
        return fig
    
    def create_evolution_timeline(self, exploration_history: List[Dict[str, Any]]) -> go.Figure:
        """Create an interactive timeline of concept evolution"""
        if not exploration_history:
            # Create sample data
            exploration_history = [
                {
                    "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "event_type": "node_created",
                    "concept": f"Concept {i+1}",
                    "content_type": "text",
                    "quality_score": random.uniform(0.6, 1.0)
                }
                for i in range(10)
            ]
        
        # Convert to dataframe structure
        timestamps = [item["timestamp"] for item in exploration_history]
        concepts = [item["concept"] for item in exploration_history]
        event_types = [item["event_type"] for item in exploration_history]
        quality_scores = [item["quality_score"] for item in exploration_history]
        
        # Create timeline visualization
        fig = go.Figure(data=go.Scatter(
            x=timestamps,
            y=quality_scores,
            mode='markers+lines',
            marker=dict(
                size=15,
                color=quality_scores,
                colorscale='RdYlGn',
                colorbar=dict(title="Quality Score"),
                showscale=True
            ),
            line=dict(color='gray', dash='dash'),
            text=[f"Concept: {c}<br>Event: {e}" for c, e in zip(concepts, event_types)],
            hovertemplate='%{text}<br>Quality: %{y:.2f}<br>Time: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Concept Evolution Timeline",
            xaxis_title="Time",
            yaxis_title="Quality Score",
            height=600,
            template='plotly_dark'
        )
        
        return fig
    
    def create_multimodal_heatmap(self, content_data: List[Dict[str, Any]]) -> go.Figure:
        """Create a heatmap showing multimodal content distribution"""
        if not content_data:
            # Create sample data
            content_types = ["text", "image", "audio", "video"]
            time_periods = [f"Day {i}" for i in range(1, 6)]
            # Create random values
            z = [[random.uniform(0, 1) for _ in time_periods] for _ in content_types]
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=time_periods,
                y=content_types,
                colorscale='Viridis'
            ))
        else:
            # Process real content data
            content_types = list(set([item["content_type"] for item in content_data if "content_type" in item]))
            concepts = list(set([item["concept"] for item in content_data if "concept" in item][:10]))  # Limit for readability
            
            # Create matrix
            z = []
            for content_type in content_types:
                row = []
                for concept in concepts:
                    # Count occurrences
                    count = len([item for item in content_data if item.get("content_type") == content_type and item.get("concept") == concept])
                    row.append(count)
                z.append(row)
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=concepts,
                y=content_types,
                colorscale='Bluered'
            ))
        
        fig.update_layout(
            title="Multimodal Content Distribution Heatmap",
            xaxis_title="Concepts",
            yaxis_title="Content Types",
            height=500,
            template='plotly_dark'
        )
        
        return fig
    
    def create_dashboard(self, exploration_id: str = "current") -> go.Figure:
        """Create a comprehensive dashboard with multiple visualizations"""
        # Create subplots - fixed to use compatible subplot types
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Knowledge Graph (2D Projection)', 'Concept Evolution', 
                          'Content Distribution', 'Quality Metrics'),
            specs=[[{"type": "xy"}, {"type": "xy"}],
                   [{"type": "heatmap"}, {"type": "bar"}]]
        )
        
        # Add 2D knowledge graph projection for compatibility
        nodes = list(self.knowledge_graph.nodes.values())
        if not nodes:
            nodes = self._create_sample_nodes()
        
        n = len(nodes)
        theta = np.linspace(0, 2 * np.pi, n)
        x = np.cos(theta)
        y = np.sin(theta)
        
        fig.add_trace(
            go.Scatter(
                x=x, y=y,
                mode='markers+text',
                marker=dict(size=12, color='lightblue'),
                text=[node.concept[:10] for node in nodes],
                textposition="top center",
                name='Concepts'
            ),
            row=1, col=1
        )
        
        # Add evolution timeline
        sample_history = [
            {
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "event_type": "node_created",
                "concept": f"Concept {i+1}",
                "content_type": "text",
                "quality_score": random.uniform(0.6, 1.0)
            }
            for i in range(10)
        ]
        
        quality_scores = [item["quality_score"] for item in sample_history]
        timestamps = [i for i in range(len(sample_history))]
        
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=quality_scores,
                mode='lines+markers',
                name='Quality Trend'
            ),
            row=1, col=2
        )
        
        # Add multimodal heatmap
        content_types = ["Text", "Image", "Audio", "Video"]
        periods = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
        z = [[random.randint(0, 10) for _ in periods] for _ in content_types]
        
        fig.add_trace(
            go.Heatmap(z=z, x=periods, y=content_types, colorscale='Viridis'),
            row=2, col=1
        )
        
        # Add quality metrics
        metrics = ["System Uptime", "Expansion Rate", "Content Quality", "Multimodal Coverage"]
        values = [99.9, 85.2, 92.1, 78.5]  # Sample values
        
        fig.add_trace(
            go.Bar(x=metrics, y=values, name='Performance Metrics'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Infinite Concept Expansion Engine - Comprehensive Dashboard",
            height=800,
            showlegend=False,
            template='plotly_dark'
        )
        
        return fig
    
    def save_visualization(self, fig: go.Figure, filename: str, format: str = "html"):
        """Save visualization to file"""
        if format == "html":
            pio.write_html(fig, f"{filename}.html", auto_open=False)
        elif format == "png":
            pio.write_image(fig, f"{filename}.png", width=1200, height=800)
        elif format == "pdf":
            pio.write_image(fig, f"{filename}.pdf", width=1200, height=800)
        
        print(f"Visualization saved as {filename}.{format}")
    
    def _create_sample_nodes(self) -> List[ConceptNode]:
        """Create sample nodes for visualization when no real data exists"""
        sample_concepts = [
            "Artificial Intelligence", "Machine Learning", "Neural Networks", 
            "Deep Learning", "Natural Language Processing", "Computer Vision",
            "Reinforcement Learning", "Data Science", "Big Data", "Cloud Computing"
        ]
        
        nodes = []
        for i, concept in enumerate(sample_concepts):
            node = ConceptNode(
                id=f"sample_node_{i}",
                concept=concept,
                content=f"Comprehensive content about {concept}",
                metadata={"sample": True, "category": "AI/ML"},
                created_at=datetime.now() - timedelta(hours=i),
                connections=[]
            )
            nodes.append(node)
        
        return nodes


class PersistentLearningSystem:
    """Enhanced learning system that persists improvements across sessions"""
    
    def __init__(self, knowledge_graph: InMemoryKnowledgeGraphEngine, feedback_system):
        self.knowledge_graph = knowledge_graph
        self.feedback_system = feedback_system
        self.learning_history = []
        self.improvement_strategies = {}
        self.performance_memory = {}
        self.persist_file = "learning_history.json"
        
        # Load any existing learning history
        self._load_persistence()
    
    def _load_persistence(self):
        """Load learning history from persistent storage"""
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, 'r') as f:
                    data = json.load(f)
                    self.learning_history = data.get('learning_history', [])
                    self.improvement_strategies = data.get('improvement_strategies', {})
                    self.performance_memory = data.get('performance_memory', {})
                    print(f"Loaded {len(self.learning_history)} learning records from persistence")
            except Exception as e:
                print(f"Error loading persistence: {e}")
    
    def _save_persistence(self):
        """Save learning history to persistent storage"""
        try:
            data = {
                'learning_history': self.learning_history,
                'improvement_strategies': self.improvement_strategies,
                'performance_memory': self.performance_memory,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.persist_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving persistence: {e}")
    
    def record_learning_event(self, event_type: str, data: Dict[str, Any]):
        """Record a learning event for long-term improvement"""
        learning_event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        self.learning_history.append(learning_event)
        
        # Update improvement strategies based on the event
        self._update_improvement_strategies(learning_event)
        
        # Persist to file
        self._save_persistence()
    
    def _update_improvement_strategies(self, event: Dict[str, Any]):
        """Update improvement strategies based on learning events"""
        event_type = event["event_type"]
        data = event["data"]
        
        if event_type == "content_quality_feedback":
            concept = data.get("concept", "unknown")
            quality_score = data.get("quality_score", 0.0)
            
            if concept not in self.improvement_strategies:
                self.improvement_strategies[concept] = {
                    "quality_history": [],
                    "improvement_count": 0
                }
            
            self.improvement_strategies[concept]["quality_history"].append(quality_score)
            
            # Calculate improvement recommendations based on history
            if len(self.improvement_strategies[concept]["quality_history"]) >= 5:
                recent_avg = np.mean(self.improvement_strategies[concept]["quality_history"][-5:])
                
                if recent_avg < 0.75:  # Quality is low
                    # Suggest improvements
                    if "suggestions" not in self.improvement_strategies[concept]:
                        self.improvement_strategies[concept]["suggestions"] = []
                    
                    suggestion = f"Quality has been below threshold. Consider enhancing content depth for {concept}."
                    if suggestion not in self.improvement_strategies[concept]["suggestions"]:
                        self.improvement_strategies[concept]["suggestions"].append(suggestion)
                        self.improvement_strategies[concept]["improvement_count"] += 1
        
        elif event_type == "connection_discovery":
            # Update strategies based on successful connections
            source = data.get("source_concept", "unknown")
            target = data.get("target_concept", "unknown")
            strength = data.get("connection_strength", 0.0)
            
            strategy_key = f"{source}-->{target}"
            if strategy_key not in self.improvement_strategies:
                self.improvement_strategies[strategy_key] = {
                    "connection_strengths": [],
                    "success_count": 0
                }
            
            self.improvement_strategies[strategy_key]["connection_strengths"].append(strength)
            if strength > 0.8:  # Strong connection
                self.improvement_strategies[strategy_key]["success_count"] += 1
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not self.learning_history:
            return {"message": "No learning history available"}
        
        # Analyze different types of events
        event_counts = {}
        quality_scores = []
        
        for event in self.learning_history:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Extract quality scores when available
            if event_type == "content_quality_feedback":
                quality_score = event["data"].get("quality_score")
                if quality_score is not None:
                    quality_scores.append(quality_score)
        
        # Calculate trends
        trends = {
            "total_learning_events": len(self.learning_history),
            "event_type_distribution": event_counts,
            "average_quality_score": np.mean(quality_scores) if quality_scores else None,
            "quality_std_deviation": np.std(quality_scores) if quality_scores else None
        }
        
        return trends
    
    def get_improvement_recommendations(self) -> List[Dict[str, str]]:
        """Get actionable improvement recommendations based on learning history"""
        recommendations = []
        
        # Analyze strategies that need improvement
        for strategy_key, strategy_data in self.improvement_strategies.items():
            if "suggestions" in strategy_data:
                for suggestion in strategy_data["suggestions"]:
                    recommendations.append({
                        "target": strategy_key,
                        "recommendation": suggestion,
                        "improvement_count": strategy_data["improvement_count"],
                        "confidence": 0.8  # High confidence for direct suggestions
                    })
        
        # Add general recommendations based on performance trends
        trends = self.get_performance_trends()
        
        if trends.get("average_quality_score", 0) < 0.8:
            recommendations.append({
                "target": "overall_content_quality",
                "recommendation": "Average quality score is below optimal. Consider implementing more rigorous validation steps.",
                "improvement_count": 0,
                "confidence": 0.6
            })
        
        return recommendations
    
    def adapt_expansion_strategy(self, strategy_name: str, performance_feedback: Dict[str, Any]):
        """Adapt expansion strategies based on performance feedback"""
        # Store performance feedback
        if strategy_name not in self.performance_memory:
            self.performance_memory[strategy_name] = []
        
        self.performance_memory[strategy_name].append({
            "timestamp": datetime.now().isoformat(),
            "feedback": performance_feedback,
            "adaptation_count": len(self.performance_memory[strategy_name])
        })
        
        # Trigger learning event
        self.record_learning_event(
            event_type="strategy_adaptation",
            data={
                "strategy_name": strategy_name,
                "performance_feedback": performance_feedback,
                "adaptation_count": len(self.performance_memory[strategy_name])
            }
        )
    
    def get_adaptive_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get adaptive parameters for a specific strategy based on learning history"""
        # Default parameters
        params = {
            "expansion_depth": 5,
            "content_diversity": 0.7,
            "validation_threshold": 0.8,
            "connection_strength_threshold": 0.6
        }
        
        if strategy_name in self.performance_memory:
            # Adjust parameters based on performance history
            performance_history = self.performance_memory[strategy_name]
            
            # If we have performance data, adapt parameters
            if performance_history:
                recent_feedback = performance_history[-1]["feedback"]
                
                # Adjust expansion depth based on quality vs quantity trade-off
                if recent_feedback.get("quality_score", 0.8) < 0.7:
                    params["expansion_depth"] = max(2, params["expansion_depth"] - 1)
                    params["validation_threshold"] = min(0.9, params["validation_threshold"] + 0.05)
                
                # Adjust diversity based on connection strength
                if recent_feedback.get("connection_strength", 0.5) < 0.6:
                    params["content_diversity"] = max(0.5, params["content_diversity"] - 0.1)
        
        return params


class RealTimeEvolutionMonitor:
    """Monitor system evolution in real-time and provide insights"""
    
    def __init__(self, knowledge_graph: InMemoryKnowledgeGraphEngine, persistent_learner: PersistentLearningSystem):
        self.knowledge_graph = knowledge_graph
        self.persistent_learner = persistent_learner
        self.evolution_metrics = {}
        self.insight_log = []
    
    def update_metrics(self):
        """Update evolution metrics"""
        current_time = datetime.now()
        
        self.evolution_metrics = {
            "timestamp": current_time.isoformat(),
            "node_count": self.knowledge_graph.get_node_count(),
            "edge_count": self.knowledge_graph.get_edge_count(),
            "growth_rate": self._calculate_growth_rate(),
            "diversity_score": self._calculate_diversity_score(),
            "connection_density": self._calculate_connection_density(),
            "learning_events_today": self._count_learning_events_today()
        }
    
    def _calculate_growth_rate(self) -> float:
        """Calculate the growth rate of the knowledge graph"""
        # In a real system, this would compare with previous measurements
        # For now, return a simulated growth rate based on node count
        node_count = self.knowledge_graph.get_node_count()
        # Simulate growth rate: more nodes = higher growth rate up to a point
        return min(1.0, node_count / 100.0)
    
    def _calculate_diversity_score(self) -> float:
        """Calculate diversity of concepts in the knowledge graph"""
        if not self.knowledge_graph.nodes:
            return 0.0
        
        concepts = [node.concept.lower() for node in self.knowledge_graph.nodes.values()]
        unique_concepts = set(concepts)
        
        # Diversity score: unique_concepts / total_concepts (clamped to 0-1)
        diversity = len(unique_concepts) / len(concepts) if concepts else 0.0
        return diversity
    
    def _calculate_connection_density(self) -> float:
        """Calculate the density of connections in the knowledge graph"""
        node_count = self.knowledge_graph.get_node_count()
        edge_count = self.knowledge_graph.get_edge_count()
        
        if node_count < 2:
            return 0.0
        
        # Maximum possible edges in a directed graph: n * (n - 1)
        max_edges = node_count * (node_count - 1)
        return edge_count / max_edges if max_edges > 0 else 0.0
    
    def _count_learning_events_today(self) -> int:
        """Count learning events from today"""
        # In a real system, this would query the persistent learner
        # For now, return a simulated count
        return len([event for event in self.persistent_learner.learning_history 
                   if datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).date() == datetime.now().date()])
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights about the system evolution"""
        self.update_metrics()
        insights = []
        
        # Insight 1: Growth Rate
        growth_rate = self.evolution_metrics["growth_rate"]
        if growth_rate > 0.8:
            insights.append({
                "type": "growth",
                "title": "Rapid Knowledge Growth",
                "description": f"The knowledge graph is expanding rapidly with a growth rate of {growth_rate:.2f}",
                "priority": "high"
            })
        elif growth_rate < 0.2:
            insights.append({
                "type": "growth",
                "title": "Slow Knowledge Growth",
                "description": f"The knowledge graph growth rate is low ({growth_rate:.2f}). Consider enhancing expansion strategies.",
                "priority": "medium"
            })
        
        # Insight 2: Diversity
        diversity = self.evolution_metrics["diversity_score"]
        if diversity > 0.8:
            insights.append({
                "type": "diversity",
                "title": "High Concept Diversity",
                "description": f"The system is exploring diverse concepts with diversity score of {diversity:.2f}",
                "priority": "low"
            })
        elif diversity < 0.5:
            insights.append({
                "type": "diversity", 
                "title": "Low Concept Diversity",
                "description": f"Concept diversity is low ({diversity:.2f}). The system may be focusing too narrowly.",
                "priority": "medium"
            })
        
        # Insight 3: Connection Density
        density = self.evolution_metrics["connection_density"]
        if density > 0.3:
            insights.append({
                "type": "connectivity",
                "title": "Well-Connected Graph",
                "description": f"The knowledge graph has good connectivity with {density:.2f} connection density",
                "priority": "low"
            })
        elif density < 0.1:
            insights.append({
                "type": "connectivity",
                "title": "Sparse Connections",
                "description": f"Connection density is low ({density:.2f}). Consider improving cross-concept linking.",
                "priority": "high"
            })
        
        # Insight 4: Learning Activity
        learning_events = self.evolution_metrics["learning_events_today"]
        if learning_events > 50:
            insights.append({
                "type": "learning",
                "title": "High Learning Activity",
                "description": f"The system has recorded {learning_events} learning events today",
                "priority": "low"
            })
        
        # Store insights
        for insight in insights:
            insight["id"] = str(uuid.uuid4())
            insight["timestamp"] = datetime.now().isoformat()
            self.insight_log.append(insight)
        
        return insights
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Get a comprehensive evolution report"""
        self.update_metrics()
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "current_metrics": self.evolution_metrics,
            "recent_insights": self.insight_log[-5:],  # Last 5 insights
            "improvement_recommendations": self.persistent_learner.get_improvement_recommendations()[:3],
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate an overall health score for the system"""
        metrics = self.evolution_metrics
        scores = []
        
        # Node count contributes to health (more nodes = healthier, to a point)
        node_score = min(1.0, metrics["node_count"] / 500.0)
        scores.append(node_score)
        
        # Growth rate contributes to health
        growth_score = metrics["growth_rate"]
        scores.append(growth_score)
        
        # Diversity contributes to health
        diversity_score = metrics["diversity_score"]
        scores.append(diversity_score)
        
        # Average all scores
        avg_score = sum(scores) / len(scores) if scores else 0.5
        
        if avg_score >= 0.8:
            return "Excellent"
        elif avg_score >= 0.6:
            return "Good"
        elif avg_score >= 0.4:
            return "Fair"
        else:
            return "Needs Attention"