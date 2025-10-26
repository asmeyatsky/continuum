#!/usr/bin/env python3
"""
Demonstration script for the Enhanced Infinite Concept Expansion Engine.
This script showcases all the powerful features of the enhanced system.
"""

import asyncio
import os
from datetime import datetime
from main import EnhancedInfiniteConceptExpansionEngine
from utils.visualization import AdvancedKnowledgeGraphVisualizer


async def demo_enhanced_features():
    """Demonstrate the enhanced features of the system"""
    print("🌟 DEMONSTRATING ENHANCED FEATURES 🌟")
    print("="*60)
    
    # Initialize the enhanced engine
    engine = EnhancedInfiniteConceptExpansionEngine()
    
    # 1. Show persistent learning loading
    print("\n💾 PERSISTENT LEARNING SYSTEM:")
    print(f"   Learning records loaded: {len(engine.persistent_learner.learning_history)}")
    print(f"   Improvement strategies: {len(engine.persistent_learner.improvement_strategies)}")
    
    # 2. Show evolution monitoring
    print("\n📈 EVOLUTION MONITORING:")
    insights = engine.evolution_monitor.generate_insights()
    print(f"   Current insights: {len(insights)}")
    for insight in insights[-2:]:  # Show last 2
        print(f"   • {insight['title']}")
    
    # 3. Run a focused expansion with enhanced features
    print("\n🔍 RUNNING ENHANCED EXPANSION:")
    concept = "Quantum Computing"
    exploration_id = await engine.expand_concept(concept, max_expansions=2)
    
    # 4. Show persistent learning in action
    print(f"\n🧠 PERSISTENT LEARNING IN ACTION:")
    print(f"   New learning events: {len([e for e in engine.persistent_learner.learning_history if e['data'].get('exploration_id') == exploration_id])}")
    
    # 5. Show evolution insights after expansion
    print(f"\n📊 EVOLUTION INSIGHTS AFTER EXPANSION:")
    report = engine.evolution_monitor.get_evolution_report()
    print(f"   System Health: {report['system_health']}")
    print(f"   Knowledge Nodes: {report['current_metrics']['node_count']}")
    print(f"   Connection Density: {report['current_metrics']['connection_density']:.2f}")
    
    # 6. Show visualization files created
    print(f"\n🎨 VISUALIZATIONS CREATED:")
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and exploration_id[:8] in f]
    for file in html_files:
        size_kb = os.path.getsize(file) // 1024
        print(f"   • {file} ({size_kb} KB)")
    
    print(f"\n   📊 Open these files in your browser to see the visualizations!")
    
    return exploration_id


def demo_continuous_learning_concept():
    """Explain the continuous learning concept"""
    print("\n" + "="*60)
    print("🔄 CONTINUOUS LEARNING MODE EXPLAINED")
    print("="*60)
    print("The Enhanced Infinite Concept Expansion Engine features a unique")
    print("continuous learning mode that makes it more powerful over time:")
    print()
    print("✅ PERSISTENT IMPROVEMENT:")
    print("   - Learning history saved across sessions")
    print("   - Improvement strategies evolve with each expansion")
    print("   - System remembers what works best for different concepts")
    print()
    print("🧠 ADAPTIVE BEHAVIOR:")
    print("   - Adjusts expansion strategies based on feedback")
    print("   - Improves content quality over time")
    print("   - Learns to make better inter-concept connections")
    print()
    print("📈 EVOLUTION TRACKING:")
    print("   - Monitors system health in real-time")
    print("   - Identifies improvement opportunities")
    print("   - Generates actionable insights for optimization")
    print()
    print("🎯 THE LONGER IT RUNS, THE BETTER IT GETS!")
    print("   Unlike traditional systems, this one continuously enhances")
    print("   its knowledge graph, content quality, and connection discovery.")


async def main():
    """Main demonstration function"""
    print("🚀🌟 ENHANCED INFINITE CONCEPT EXPANSION ENGINE 🌟🚀")
    print("   Advanced Features Demonstration")
    print("="*60)
    
    # Run the enhanced features demo
    exploration_id = await demo_enhanced_features()
    
    # Explain continuous learning
    demo_continuous_learning_concept()
    
    print(f"\n✨ DEMONSTRATION COMPLETE!")
    print(f"   Exploration ID: {exploration_id}")
    print(f"   Check the visualization files in your project directory")
    print(f"   Learning history saved in learning_history.json")
    print(f"   The system is now smarter than when it started! 🧠")


if __name__ == "__main__":
    asyncio.run(main())