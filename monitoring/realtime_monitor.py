"""
Real-Time Monitoring and Alerting System

Continuously monitors information streams, detects significant changes,
and sends alerts for important events and trends.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from data_pipeline.real_ingestion import ComprehensiveDataPipeline
from config.settings import settings

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    TRENDING = "trending"

@dataclass
class Alert:
    """Real-time alert data structure"""
    id: str
    level: AlertLevel
    title: str
    description: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    related_concepts: List[str] = field(default_factory=list)

@dataclass 
class MonitoringConfig:
    """Configuration for monitoring system"""
    topics: List[str]
    sources: List[str]
    alert_threshold: float = 0.8
    check_interval_minutes: int = 5
    trend_window_hours: int = 24
    min_sources_for_trend: int = 3

class RealTimeMonitor:
    """
    Real-time monitoring system that continuously watches information streams
    """
    
    def __init__(self, data_pipeline: ComprehensiveDataPipeline):
        self.data_pipeline = data_pipeline
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.monitoring_configs: Dict[str, MonitoringConfig] = {}
        self.historical_data: Dict[str, List[Dict]] = {}
        self.trends: Dict[str, Dict] = {}
        self.is_running = False
        
    async def start_monitoring(self, config: MonitoringConfig) -> str:
        """Start monitoring for specific topics and sources"""
        monitor_id = hashlib.md5(
            f"{','.join(config.topics)}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        self.monitoring_configs[monitor_id] = config
        self.historical_data[monitor_id] = []
        
        logger.info(f"🔍 Starting real-time monitoring: {monitor_id} for topics: {config.topics}")
        
        # Start background monitoring task
        asyncio.create_task(self._monitoring_loop(monitor_id))
        
        return monitor_id
    
    async def stop_monitoring(self, monitor_id: str):
        """Stop specific monitoring session"""
        if monitor_id in self.monitoring_configs:
            del self.monitoring_configs[monitor_id]
            del self.historical_data[monitor_id]
            logger.info(f"⏹️ Stopped monitoring: {monitor_id}")
    
    async def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    async def _monitoring_loop(self, monitor_id: str):
        """Main monitoring loop for a specific configuration"""
        config = self.monitoring_configs[monitor_id]
        
        while monitor_id in self.monitoring_configs and self.is_running:
            try:
                # Check all topics
                for topic in config.topics:
                    await self._monitor_topic(topic, config, monitor_id)
                
                # Wait for next check
                await asyncio.sleep(config.check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Monitoring error for {monitor_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _monitor_topic(self, topic: str, config: MonitoringConfig, monitor_id: str):
        """Monitor a specific topic for changes and trends"""
        logger.debug(f"🔍 Monitoring topic: {topic}")
        
        # Gather current data
        current_time = datetime.now()
        results = await self.data_pipeline.comprehensive_search(topic, config.sources)
        
        # Analyze for alerts
        alerts = await self._analyze_for_alerts(topic, results, config)
        
        # Store historical data
        self.historical_data[monitor_id].append({
            'timestamp': current_time,
            'topic': topic,
            'results': results,
            'alerts': [alert.id for alert in alerts]
        })
        
        # Clean old historical data
        cutoff_time = current_time - timedelta(hours=config.trend_window_hours)
        self.historical_data[monitor_id] = [
            h for h in self.historical_data[monitor_id] 
            if h['timestamp'] > cutoff_time
        ]
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _analyze_for_alerts(self, topic: str, results: Dict[str, Any], 
                                config: MonitoringConfig) -> List[Alert]:
        """Analyze monitoring results for alert conditions"""
        alerts = []
        
        # Check for trending content
        trend_alerts = await self._detect_trends(topic, results, config)
        alerts.extend(trend_alerts)
        
        # Check for breaking news
        news_alerts = await self._detect_breaking_news(topic, results)
        alerts.extend(news_alerts)
        
        # Check for academic breakthroughs
        academic_alerts = await self._detect_academic_breakthroughs(topic, results)
        alerts.extend(academic_alerts)
        
        # Check for viral social content
        viral_alerts = await self._detect_viral_content(topic, results)
        alerts.extend(viral_alerts)
        
        return alerts
    
    async def _detect_trends(self, topic: str, results: Dict[str, Any], 
                           config: MonitoringConfig) -> List[Alert]:
        """Detect trending topics across multiple sources"""
        alerts = []
        
        # Count mentions across sources
        total_mentions = 0
        source_count = 0
        source_details = {}
        
        for source, result in results.items():
            if result.success and result.data:
                mention_count = len(result.data)
                source_details[source] = mention_count
                total_mentions += mention_count
                source_count += 1
        
        # Check if trending (appears in multiple sources with significant content)
        if source_count >= config.min_sources_for_trend and total_mentions > 10:
            trend_score = (source_count / len(config.sources)) * (total_mentions / 50)
            
            if trend_score > config.alert_threshold:
                alert = Alert(
                    id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    level=AlertLevel.TRENDING,
                    title=f"🔥 Trending: {topic}",
                    description=f"Topic '{topic}' is trending across {source_count} sources with {total_mentions} mentions",
                    source="trend_detection",
                    timestamp=datetime.now(),
                    metadata={
                        'source_count': source_count,
                        'total_mentions': total_mentions,
                        'source_details': source_details,
                        'trend_score': trend_score
                    },
                    keywords=[topic],
                    confidence=trend_score
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_breaking_news(self, topic: str, results: Dict[str, Any]) -> List[Alert]:
        """Detect breaking news related to topic"""
        alerts = []
        
        if 'news' in results and results['news'].success:
            news_items = results['news'].data
            
            # Look for recent breaking news indicators
            breaking_keywords = ['breaking', 'urgent', 'developing', 'just in', 'alert']
            current_time = datetime.now()
            
            for item in news_items[:3]:  # Check top 3 items
                title = item.get('title', '').lower()
                description = item.get('description', '').lower()
                
                # Check for breaking indicators
                if any(keyword in title or keyword in description for keyword in breaking_keywords):
                    alert = Alert(
                        id=f"breaking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        level=AlertLevel.CRITICAL,
                        title=f"🚨 Breaking News: {topic}",
                        description=f"Breaking news detected: {item.get('title', '')}",
                        source="news_monitor",
                        timestamp=current_time,
                        metadata={
                            'news_item': item,
                            'source': item.get('source', ''),
                            'url': item.get('url', '')
                        },
                        keywords=[topic, 'breaking'],
                        confidence=0.9
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _detect_academic_breakthroughs(self, topic: str, results: Dict[str, Any]) -> List[Alert]:
        """Detect potential academic breakthroughs"""
        alerts = []
        
        academic_sources = ['academic', 'arxiv']
        breakthrough_keywords = [
            'breakthrough', 'novel', 'revolutionary', 'first time', 
            'discovery', 'innovation', 'paradigm shift'
        ]
        
        for source in academic_sources:
            if source in results and results[source].success:
                papers = results[source].data
                
                for paper in papers[:2]:  # Check top 2 papers
                    title = paper.get('title', '').lower()
                    abstract = paper.get('abstract', '').lower()
                    
                    # Check for breakthrough indicators
                    if any(keyword in title or keyword in abstract for keyword in breakthrough_keywords):
                        alert = Alert(
                            id=f"academic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            level=AlertLevel.WARNING,
                            title=f"🔬 Academic Breakthrough: {topic}",
                            description=f"Potential breakthrough: {paper.get('title', '')}",
                            source="academic_monitor",
                            timestamp=datetime.now(),
                            metadata={
                                'paper': paper,
                                'source': source,
                                'arxiv_id': paper.get('arxiv_id', ''),
                                'url': paper.get('url', '')
                            },
                            keywords=[topic, 'breakthrough', 'research'],
                            confidence=0.8
                        )
                        alerts.append(alert)
        
        return alerts
    
    async def _detect_viral_content(self, topic: str, results: Dict[str, Any]) -> List[Alert]:
        """Detect viral content on social platforms"""
        alerts = []
        
        viral_sources = ['reddit', 'youtube']
        
        for source in viral_sources:
            if source in results and results[source].success:
                content_items = results[source].data
                
                for item in content_items[:3]:  # Check top 3 items
                    # Look for high engagement metrics
                    engagement_score = 0
                    
                    if source == 'reddit':
                        score = item.get('score', 0)
                        comments = item.get('num_comments', 0)
                        engagement_score = (score + comments * 2) / 1000  # Normalize
                    
                    elif source == 'youtube':
                        views = item.get('view_count', 0)
                        likes = item.get('like_count', 0)
                        engagement_score = (views + likes * 10) / 100000  # Normalize
                    
                    # Consider viral if engagement is high
                    if engagement_score > 0.5:  # 500+ engagement points
                        alert = Alert(
                            id=f"viral_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            level=AlertLevel.TRENDING,
                            title=f"📈 Viral Content: {topic}",
                            description=f"Viral content detected on {source}: {item.get('title', '')[:100]}",
                            source="viral_monitor",
                            timestamp=datetime.now(),
                            metadata={
                                'item': item,
                                'platform': source,
                                'engagement_score': engagement_score
                            },
                            keywords=[topic, 'viral', source],
                            confidence=min(engagement_score, 1.0)
                        )
                        alerts.append(alert)
        
        return alerts
    
    async def _send_alert(self, alert: Alert):
        """Send alert through all configured channels"""
        # Store alert
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log alert
        logger.info(f"🚨 ALERT [{alert.level.value.upper()}] {alert.title}")
        
        # Call all registered callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def get_recent_alerts(self, hours: int = 24, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get recent alerts within specified timeframe"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alerts 
            if alert.timestamp > cutoff_time
        ]
        
        if level:
            recent_alerts = [alert for alert in recent_alerts if alert.level == level]
        
        return recent_alerts
    
    def get_trending_topics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get currently trending topics based on alert frequency"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
        
        # Count keyword frequencies
        keyword_counts = {}
        for alert in recent_alerts:
            for keyword in alert.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency
        trending = sorted(
            [{'topic': kw, 'count': count} for kw, count in keyword_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        return trending[:10]  # Top 10 trending topics
    
    async def start_global_monitoring(self):
        """Start the global monitoring system"""
        self.is_running = True
        logger.info("🌍 Starting global real-time monitoring system")
    
    async def stop_global_monitoring(self):
        """Stop the global monitoring system"""
        self.is_running = False
        logger.info("⏹️ Stopped global real-time monitoring system")

# Default alert callback implementations
class ConsoleAlertCallback:
    """Print alerts to console"""
    
    async def __call__(self, alert: Alert):
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️", 
            AlertLevel.CRITICAL: "🚨",
            AlertLevel.TRENDING: "🔥"
        }
        
        emoji = emoji_map.get(alert.level, "📢")
        print(f"\n{emoji} [{alert.level.value.upper()}] {alert.title}")
        print(f"   {alert.description}")
        print(f"   Source: {alert.source} | Confidence: {alert.confidence:.2f}")
        print(f"   Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

class WebhookAlertCallback:
    """Send alerts to webhook endpoint"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def __call__(self, alert: Alert):
        import aiohttp
        
        payload = {
            'id': alert.id,
            'level': alert.level.value,
            'title': alert.title,
            'description': alert.description,
            'source': alert.source,
            'timestamp': alert.timestamp.isoformat(),
            'metadata': alert.metadata,
            'keywords': alert.keywords,
            'confidence': alert.confidence
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Alert sent to webhook: {alert.id}")
        except Exception as e:
            logger.error(f"Webhook alert failed: {e}")