"""
Self-Improving Feedback System for the Infinite Concept Expansion Engine.

This module implements continuous learning from system performance and user interactions
with feedback loops, online learning, and improvement mechanisms.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime
import json
import statistics


@dataclass
class FeedbackRecord:
    """A single feedback record from a user or system evaluation"""
    id: str
    feedback_type: str  # "user_rating", "engagement", "quality", "accuracy", "relevance"
    item_id: str  # ID of the item being rated
    rating: float  # 0.0 to 1.0 scale
    comment: Optional[str]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class LearningSignal:
    """A learning signal for the improvement system"""
    id: str
    signal_type: str  # "positive", "negative", "neutral", "pattern", "anomaly"
    content: Any
    confidence: float
    source: str
    timestamp: datetime


class FeedbackSystem(ABC):
    """Abstract base class for the feedback system"""
    
    @abstractmethod
    def record_user_feedback(self, item_id: str, rating: float, comment: Optional[str] = None) -> bool:
        """Record user feedback for an item"""
        pass
    
    @abstractmethod
    def record_system_feedback(self, feedback_type: str, item_id: str, rating: float, metadata: Dict[str, Any]) -> bool:
        """Record system-generated feedback"""
        pass
    
    @abstractmethod
    def get_feedback_summary(self, item_id: str) -> Dict[str, Any]:
        """Get summary of feedback for an item"""
        pass
    
    @abstractmethod
    def get_learning_signals(self) -> List[LearningSignal]:
        """Get accumulated learning signals for improvement"""
        pass


class SelfImprovingFeedbackSystem(FeedbackSystem):
    """Implementation of the self-improving feedback system"""
    
    def __init__(self):
        self.feedback_records: List[FeedbackRecord] = []
        self.learning_signals: List[LearningSignal] = []
        self.expansion_strategies: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
    
    def record_user_feedback(self, item_id: str, rating: float, comment: Optional[str] = None) -> bool:
        """Record user feedback for an item"""
        if not 0.0 <= rating <= 1.0:
            return False
        
        feedback = FeedbackRecord(
            id=str(uuid.uuid4()),
            feedback_type="user_rating",
            item_id=item_id,
            rating=rating,
            comment=comment,
            metadata={"feedback_source": "user"},
            timestamp=datetime.now()
        )
        
        self.feedback_records.append(feedback)
        
        # Generate learning signals based on feedback
        self._process_feedback_for_learning(feedback)
        
        return True
    
    def record_system_feedback(self, feedback_type: str, item_id: str, rating: float, metadata: Dict[str, Any]) -> bool:
        """Record system-generated feedback"""
        if not 0.0 <= rating <= 1.0:
            return False
        
        feedback = FeedbackRecord(
            id=str(uuid.uuid4()),
            feedback_type=feedback_type,
            item_id=item_id,
            rating=rating,
            comment=None,
            metadata=metadata,
            timestamp=datetime.now()
        )
        
        self.feedback_records.append(feedback)
        
        # Generate learning signals based on feedback
        self._process_feedback_for_learning(feedback)
        
        return True
    
    def get_feedback_summary(self, item_id: str) -> Dict[str, Any]:
        """Get summary of feedback for an item"""
        item_feedback = [f for f in self.feedback_records if f.item_id == item_id]
        
        if not item_feedback:
            return {
                "item_id": item_id,
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
                "recent_feedback": []
            }
        
        ratings = [f.rating for f in item_feedback]
        feedback_types = [f.feedback_type for f in item_feedback]
        
        # Calculate distribution
        rating_distribution = {}
        for rating in ratings:
            rounded_rating = round(rating, 1)  # Round to 1 decimal place
            rating_distribution[rounded_rating] = rating_distribution.get(rounded_rating, 0) + 1
        
        return {
            "item_id": item_id,
            "total_feedback": len(item_feedback),
            "average_rating": statistics.mean(ratings),
            "median_rating": statistics.median(ratings),
            "rating_distribution": rating_distribution,
            "feedback_types": list(set(feedback_types)),
            "recent_feedback": item_feedback[-5:]  # Last 5 feedback entries
        }
    
    def get_learning_signals(self) -> List[LearningSignal]:
        """Get accumulated learning signals for improvement"""
        return self.learning_signals
    
    def _process_feedback_for_learning(self, feedback: FeedbackRecord):
        """Process feedback to generate learning signals"""
        # Determine signal type based on rating
        if feedback.rating >= 0.8:
            signal_type = "positive"
        elif feedback.rating <= 0.3:
            signal_type = "negative"
        else:
            signal_type = "neutral"
        
        # Create learning signal
        signal = LearningSignal(
            id=str(uuid.uuid4()),
            signal_type=signal_type,
            content=feedback,
            confidence=abs(feedback.rating - 0.5) * 2,  # Higher confidence for ratings further from 0.5
            source=feedback.feedback_type,
            timestamp=feedback.timestamp
        )
        
        self.learning_signals.append(signal)
        
        # Update performance metrics
        if feedback.feedback_type not in self.performance_metrics:
            self.performance_metrics[feedback.feedback_type] = []
        
        self.performance_metrics[feedback.feedback_type].append(feedback.rating)
    
    def analyze_expansion_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in exploration expansions to improve strategy"""
        pattern_analysis = {
            "most_successful_expansion_types": {},
            "common_patterns": [],
            "improvement_opportunities": [],
            "strategy_effectiveness": {}
        }
        
        # Analyze feedback by expansion type
        feedback_by_type = {}
        for feedback in self.feedback_records:
            # Extract expansion type from metadata if available
            exp_type = feedback.metadata.get("expansion_type", "unknown")
            if exp_type not in feedback_by_type:
                feedback_by_type[exp_type] = []
            feedback_by_type[exp_type].append(feedback.rating)
        
        # Calculate average ratings for each expansion type
        for exp_type, ratings in feedback_by_type.items():
            if ratings:
                avg_rating = statistics.mean(ratings)
                pattern_analysis["most_successful_expansion_types"][exp_type] = avg_rating
        
        # Identify common patterns in high/low rated feedback
        high_rated = [f for f in self.feedback_records if f.rating >= 0.8]
        low_rated = [f for f in self.feedback_records if f.rating <= 0.3]
        
        if high_rated:
            pattern_analysis["common_patterns"].append({
                "type": "high_rated_characteristics",
                "data": self._extract_common_features(high_rated)
            })
        
        if low_rated:
            pattern_analysis["improvement_opportunities"].append({
                "type": "low_rated_issues",
                "data": self._extract_common_features(low_rated)
            })
        
        return pattern_analysis
    
    def _extract_common_features(self, feedback_list: List[FeedbackRecord]) -> Dict[str, Any]:
        """Extract common features from feedback records"""
        # This would be a more sophisticated analysis in a real system
        # For now, just return basic statistics
        if not feedback_list:
            return {}
        
        ratings = [f.rating for f in feedback_list]
        sources = [f.feedback_type for f in feedback_list]
        
        return {
            "average_rating": statistics.mean(ratings),
            "rating_std_dev": statistics.stdev(ratings) if len(ratings) > 1 else 0,
            "common_sources": statistics.mode(sources) if sources else None,
            "total_samples": len(feedback_list)
        }
    
    def update_expansion_strategy(self, strategy_id: str, performance_data: Dict[str, Any]) -> bool:
        """Update an expansion strategy based on performance data"""
        if strategy_id not in self.expansion_strategies:
            self.expansion_strategies[strategy_id] = {
                "strategy_id": strategy_id,
                "update_history": [],
                "effectiveness_score": 0.0
            }
        
        update_record = {
            "timestamp": datetime.now(),
            "performance_data": performance_data,
            "improvements_applied": []
        }
        
        # Calculate new effectiveness score
        if "ratings" in performance_data and performance_data["ratings"]:
            scores = performance_data["ratings"]
            new_score = statistics.mean(scores)
            self.expansion_strategies[strategy_id]["effectiveness_score"] = new_score
        
        self.expansion_strategies[strategy_id]["update_history"].append(update_record)
        
        # Apply improvement recommendations based on performance
        self._apply_improvements(strategy_id, performance_data)
        
        return True
    
    def _apply_improvements(self, strategy_id: str, performance_data: Dict[str, Any]):
        """Apply specific improvements to a strategy based on performance data"""
        improvements = self.expansion_strategies[strategy_id].get("improvements_applied", [])
        
        # Example improvement logic
        if performance_data.get("average_rating", 0) < 0.6:
            improvements.append("increase_content_depth")
        
        if performance_data.get("engagement_rate", 0) < 0.3:
            improvements.append("improve_multimodal_content_ratio")
        
        if performance_data.get("accuracy_issues", 0) > 0.1:
            improvements.append("enhance_validation_steps")
        
        self.expansion_strategies[strategy_id]["improvements_applied"] = improvements
    
    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for system improvements"""
        recommendations = []
        
        # Analyze performance metrics
        for feedback_type, ratings in self.performance_metrics.items():
            if ratings:
                avg_rating = statistics.mean(ratings)
                if avg_rating < 0.7:
                    recommendations.append({
                        "target": f"{feedback_type} feedback",
                        "issue": f"Average rating of {avg_rating:.2f} is below threshold",
                        "recommendation": f"Focus improvement efforts on {feedback_type} related features",
                        "priority": "high" if avg_rating < 0.5 else "medium"
                    })
        
        # Add recommendations based on learning signals
        negative_signals = [s for s in self.learning_signals if s.signal_type == "negative"]
        if negative_signals:
            recommendations.append({
                "target": "overall_system",
                "issue": f"{len(negative_signals)} negative signals detected",
                "recommendation": "Review system components generating negative feedback",
                "priority": "high"
            })
        
        return recommendations


class PerformanceMonitor:
    """Monitor system performance and generate metrics for feedback"""
    
    def __init__(self, feedback_system: FeedbackSystem):
        self.feedback_system = feedback_system
        self.metrics: Dict[str, List[float]] = {}
    
    def log_metric(self, metric_name: str, value: float):
        """Log a performance metric"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
    
    def generate_system_feedback(self):
        """Generate system feedback based on performance metrics"""
        if not self.metrics:
            return
        
        for metric_name, values in self.metrics.items():
            if values:
                avg_value = sum(values) / len(values)
                # Convert performance metrics to feedback ratings (0-1 scale)
                # This is a simplified conversion - real implementation would be more nuanced
                rating = min(1.0, max(0.0, avg_value))  # Clamp between 0 and 1
                
                self.feedback_system.record_system_feedback(
                    feedback_type=metric_name,
                    item_id=f"system_{metric_name}",
                    rating=rating,
                    metadata={
                        "average_value": avg_value,
                        "sample_count": len(values),
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        # Clear metrics after generating feedback
        self.metrics = {}