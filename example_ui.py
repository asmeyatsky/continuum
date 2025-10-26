"""
Example usage of the UI components for the Infinite Concept Expansion Engine.
"""
from ui.components import UIDashboard, InputInterface, OutputRenderer


def main():
    """Demonstrate the UI components"""
    print("🎨 Infinite Concept Expansion Engine - UI Components Demo")
    print("="*60)
    
    # Initialize UI components
    dashboard = UIDashboard()
    input_interface = InputInterface() 
    output_renderer = OutputRenderer()
    
    # Show dashboard
    print("\n📊 Dashboard View:")
    dashboard_data = dashboard.render_dashboard()
    print(f"  Title: {dashboard_data['title']}")
    print(f"  Active Explorations: {dashboard_data['metrics']['active_explorations']}")
    print(f"  System Status: {dashboard_data['system_status']}")
    
    # Show input interface
    print("\n📝 Input Interface:")
    input_form = input_interface.render_input_form()
    print(f"  Form Title: {input_form['title']}")
    print(f"  Fields: {len(input_form['fields'])}")
    print(f"  Buttons: {[btn['label'] for btn in input_form['buttons']]}")
    
    # Simulate concept submission
    concept_data = {
        "concept_description": "Renewable Energy Technologies",
        "exploration_depth": 5,
        "focus_areas": ["research", "applications", "future"]
    }
    
    print(f"\n🔍 Submitting concept: {concept_data['concept_description']}")
    submission_result = input_interface.handle_concept_submission(concept_data)
    print(f"  Success: {submission_result['success']}")
    print(f"  Exploration ID: {submission_result['exploration_id']}")
    print(f"  Message: {submission_result['message']}")
    
    # Show output rendering
    print(f"\n📤 Output Rendering (Adaptive Layout):")
    output = output_renderer.render_exploration_results(submission_result['exploration_id'], "adaptive")
    print(f"  Layout Type: {output['layout_type']}")
    print(f"  Content Groups: {len(output['content_groups'])}")
    
    for group in output['content_groups']:
        print(f"    - {group['type']}: {group['title']}")
    
    print(f"\n📖 Output Rendering (Reading Layout):")
    reading_output = output_renderer.render_exploration_results(submission_result['exploration_id'], "reading")
    print(f"  Layout Type: {reading_output['layout_type']}")
    print(f"  Sections: {len(reading_output['content']['sections'])}")
    
    print(f"\n📽️  Output Rendering (Presentation Layout):")
    presentation_output = output_renderer.render_exploration_results(submission_result['exploration_id'], "presentation")
    print(f"  Layout Type: {presentation_output['layout_type']}")
    print(f"  Slides: {len(presentation_output['slides'])}")
    
    # Show specific dashboard components
    print(f"\n📋 Dashboard Components for Exploration {submission_result['exploration_id']}:")
    canvas_data = dashboard.get_concept_canvas_data(submission_result['exploration_id'])
    print(f"  Canvas Nodes: {len(canvas_data['nodes'])}")
    print(f"  Canvas Edges: {len(canvas_data['edges'])}")
    
    feed_data = dashboard.get_live_expansion_feed(submission_result['exploration_id'])
    print(f"  Live Feed Items: {len(feed_data)}")
    
    gallery_data = dashboard.get_media_gallery(submission_result['exploration_id'])
    print(f"  Media Gallery Items: {len(gallery_data['assets'])}")
    
    print("\n" + "="*60)
    print("✅ UI Components Demo Completed!")


if __name__ == "__main__":
    main()