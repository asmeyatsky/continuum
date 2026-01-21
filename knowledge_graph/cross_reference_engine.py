"""
Cross-Referencing and Fact Verification System

Enhances knowledge graph with automated fact-checking, source verification,
and cross-reference analysis to ensure information accuracy and reliability.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
from collections import defaultdict

from knowledge_graph.engine import InMemoryKnowledgeGraphEngine, ConceptNode, GraphEdge
from data_pipeline.real_ingestion import ComprehensiveDataPipeline

logger = logging.getLogger(__name__)

class ReliabilityScore(Enum):
    """Source reliability levels"""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
    UNKNOWN = "unknown"

class FactStatus(Enum):
    """Fact verification status"""
    VERIFIED = "verified"
    DISPUTED = "disputed"
    UNVERIFIED = "unverified"
    DEBUNKED = "debunked"

@dataclass
class SourceReliability:
    """Reliability rating for information sources"""
    source: str
    reliability: ReliabilityScore
    confidence: float
    verification_count: int
    last_updated: datetime

@dataclass
class FactCheck:
    """Result of fact verification"""
    claim: str
    status: FactStatus
    confidence: float
    supporting_sources: List[str] = field(default_factory=list)
    contradicting_sources: List[str] = field(default_factory=list)
    verification_metadata: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)

class CrossReferenceEngine:
    """
    Advanced cross-referencing and fact verification system
    """
    
    def __init__(self, knowledge_graph: InMemoryKnowledgeGraphEngine, 
                 data_pipeline: ComprehensiveDataPipeline):
        self.knowledge_graph = knowledge_graph
        self.data_pipeline = data_pipeline
        self.source_reliability: Dict[str, SourceReliability] = {}
        self.fact_checks: Dict[str, FactCheck] = {}
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)
        
        # Initialize source reliability ratings
        self._initialize_source_reliability()
    
    def _initialize_source_reliability(self):
        """Initialize reliability ratings for common sources"""
        high_reliability_sources = [
            'pubmed', 'arxiv', 'nature', 'science', 'academic',
            'wikipedia', 'reuters', 'ap', 'bbc'
        ]
        
        medium_reliability_sources = [
            'github', 'stackoverflow', 'news', 'youtube', 'reddit'
        ]
        
        for source in high_reliability_sources:
            self.source_reliability[source] = SourceReliability(
                source=source,
                reliability=ReliabilityScore.HIGH,
                confidence=0.9,
                verification_count=0,
                last_updated=datetime.now()
            )
        
        for source in medium_reliability_sources:
            self.source_reliability[source] = SourceReliability(
                source=source,
                reliability=ReliabilityScore.MEDIUM,
                confidence=0.7,
                verification_count=0,
                last_updated=datetime.now()
            )
    
    async def verify_fact(self, claim: str, context: Optional[Dict] = None) -> FactCheck:
        """Verify a factual claim across multiple sources"""
        logger.info(f"🔍 Verifying fact: {claim[:100]}...")
        
        # Extract key terms for search
        key_terms = self._extract_key_terms(claim)
        
        # Search for supporting and contradicting information
        search_query = " ".join(key_terms)
        results = await self.data_pipeline.comprehensive_search(
            search_query,
            sources=['academic', 'wikipedia', 'news', 'web_search']
        )
        
        # Analyze results for fact verification
        supporting_sources = []
        contradicting_sources = []
        total_relevance = 0
        total_confidence = 0
        
        for source, result in results.items():
            if result.success and result.data:
                source_analysis = await self._analyze_source_for_fact(
                    claim, result.data, source
                )
                
                if source_analysis['supports']:
                    supporting_sources.extend(source_analysis['sources'])
                    total_relevance += source_analysis['relevance']
                    total_confidence += source_analysis['confidence']
                elif source_analysis['contradicts']:
                    contradicting_sources.extend(source_analysis['sources'])
        
        # Determine fact status
        fact_check_id = hashlib.md5(claim.encode()).hexdigest()[:16]
        
        if len(supporting_sources) > len(contradicting_sources):
            if total_confidence / max(len(supporting_sources), 1) > 0.8:
                status = FactStatus.VERIFIED
            else:
                status = FactStatus.UNVERIFIED
        elif len(contradicting_sources) > len(supporting_sources):
            status = FactStatus.DEBUNKED
        else:
            status = FactStatus.DISPUTED
        
        fact_check = FactCheck(
            claim=claim,
            status=status,
            confidence=min(total_confidence / max(len(supporting_sources), 1), 1.0),
            supporting_sources=list(set(supporting_sources)),
            contradicting_sources=list(set(contradicting_sources)),
            verification_metadata={
                'search_terms': key_terms,
                'sources_searched': list(results.keys()),
                'total_relevance': total_relevance
            }
        )
        
        # Store fact check
        self.fact_checks[fact_check_id] = fact_check
        
        logger.info(f"✅ Fact verified: {claim[:50]}... -> {status.value}")
        return fact_check
    
    async def cross_reference_node(self, node_id: str) -> Dict[str, Any]:
        """Cross-reference a knowledge graph node with other sources"""
        node = self.knowledge_graph.nodes.get(node_id)
        if not node:
            return {"error": "Node not found"}
        
        logger.info(f"🔗 Cross-referencing node: {node.concept}")
        
        # Find similar concepts across sources
        cross_refs = await self._find_cross_references(node)
        
        # Verify claims in the node content
        claims = self._extract_claims_from_content(node.content)
        verified_claims = []
        
        for claim in claims:
            fact_check = await self.verify_fact(claim, {"node_id": node_id})
            verified_claims.append(fact_check)
        
        # Calculate overall reliability score
        reliability_score = self._calculate_node_reliability(
            node, cross_refs, verified_claims
        )
        
        # Update node with cross-reference information
        updated_metadata = {
            **node.metadata,
            'cross_references': cross_refs,
            'fact_checks': [fc.claim for fc in verified_claims],
            'reliability_score': reliability_score,
            'last_verified': datetime.now().isoformat()
        }
        
        # Update knowledge graph node
        node.metadata.update(updated_metadata)
        
        return {
            'node_id': node_id,
            'concept': node.concept,
            'cross_references': cross_refs,
            'verified_claims': len([fc for fc in verified_claims if fc.status == FactStatus.VERIFIED]),
            'total_claims': len(verified_claims),
            'reliability_score': reliability_score,
            'verification_timestamp': datetime.now().isoformat()
        }
    
    async def detect_contradictions(self) -> List[Dict[str, Any]]:
        """Detect contradictions within the knowledge graph"""
        logger.info("🔍 Detecting contradictions in knowledge graph...")
        
        contradictions = []
        nodes = list(self.knowledge_graph.nodes.values())
        
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                # Check for similar concepts
                similarity = self._calculate_concept_similarity(node1.concept, node2.concept)
                
                if similarity > 0.7:  # High similarity threshold
                    # Check for contradictory claims
                    claims1 = self._extract_claims_from_content(node1.content)
                    claims2 = self._extract_claims_from_content(node2.content)
                    
                    contradictory_pairs = self._find_contradictory_claims(claims1, claims2)
                    
                    if contradictory_pairs:
                        contradictions.append({
                            'node1_id': node1.id,
                            'node2_id': node2.id,
                            'concept1': node1.concept,
                            'concept2': node2.concept,
                            'similarity': similarity,
                            'contradictory_claims': contradictory_pairs
                        })
        
        logger.info(f"Found {len(contradictions)} potential contradictions")
        return contradictions
    
    async def strengthen_connections(self, node_id: str) -> List[GraphEdge]:
        """Find and add stronger connections to a node based on cross-references"""
        node = self.knowledge_graph.nodes.get(node_id)
        if not node:
            return []
        
        logger.info(f"💪 Strengthening connections for: {node.concept}")
        
        # Find related concepts through cross-referencing
        related_concepts = await self._discover_related_concepts(node)
        
        # Create or strengthen edges
        new_edges = []
        for related in related_concepts:
            # Find existing node or create new one
            target_node_id = None
            for existing_node in self.knowledge_graph.nodes.values():
                if self._calculate_concept_similarity(
                    existing_node.concept, related['concept']
                ) > 0.8:
                    target_node_id = existing_node.id
                    break
            
            if target_node_id:
                # Create or strengthen edge
                edge_id = f"{node_id}_{target_node_id}"
                
                edge = GraphEdge(
                    id=edge_id,
                    source_node_id=node_id,
                    target_node_id=target_node_id,
                    relationship_type="cross_reference",
                    weight=related['confidence'],
                    created_at=datetime.now(),
                    metadata={
                        'cross_reference_source': related['source'],
                        'verification_method': 'automated_cross_ref'
                    }
                )
                
                new_edges.append(edge)
        
        return new_edges
    
    async def _find_cross_references(self, node: ConceptNode) -> List[Dict[str, Any]]:
        """Find cross-references for a node across multiple sources"""
        cross_refs = []
        
        # Search for the concept across different sources
        results = await self.data_pipeline.comprehensive_search(
            node.concept,
            sources=['academic', 'wikipedia', 'news', 'web_search', 'github']
        )
        
        for source, result in results.items():
            if result.success and result.data:
                # Analyze content for relevance
                for item in result.data[:3]:  # Top 3 items per source
                    relevance = self._calculate_content_relevance(node, item)
                    
                    if relevance > 0.6:  # Relevance threshold
                        cross_refs.append({
                            'source': source,
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'content_snippet': item.get('content', item.get('description', ''))[:200],
                            'relevance': relevance,
                            'source_reliability': self.source_reliability.get(
                                source, 
                                SourceReliability(source, ReliabilityScore.UNKNOWN, 0.5, 0, datetime.now())
                            ).reliability.value
                        })
        
        return sorted(cross_refs, key=lambda x: x['relevance'], reverse=True)
    
    async def _analyze_source_for_fact(self, claim: str, data: List[Dict], 
                                     source: str) -> Dict[str, Any]:
        """Analyze a source's content for fact verification"""
        supports = []
        contradicts = []
        total_relevance = 0
        total_confidence = 0
        
        for item in data:
            content = (
                item.get('title', '') + ' ' + 
                item.get('content', item.get('description', item.get('abstract', '')))
            ).lower()
            
            # Simple keyword matching for support/contradiction
            support_keywords = ['confirms', 'verifies', 'proves', 'shows', 'demonstrates']
            contradict_keywords = ['disproves', 'contradicts', 'refutes', 'debunks', 'disagrees']
            
            claim_lower = claim.lower()
            
            # Check for supporting evidence
            if any(keyword in content for keyword in support_keywords):
                supports.append(item['url'] if 'url' in item else source)
                total_relevance += 0.8
                total_confidence += self.source_reliability.get(
                    source, 
                    SourceReliability(source, ReliabilityScore.UNKNOWN, 0.5, 0, datetime.now())
                ).confidence
            
            # Check for contradicting evidence
            elif any(keyword in content for keyword in contradict_keywords):
                contradicts.append(item['url'] if 'url' in item else source)
                total_relevance += 0.7
                total_confidence += self.source_reliability.get(
                    source, 
                    SourceReliability(source, ReliabilityScore.UNKNOWN, 0.5, 0, datetime.now())
                ).confidence
            
            # Check for mention without clear stance
            elif claim_lower in content or any(word in content for word in claim_lower.split()[:3]):
                total_relevance += 0.5
        
        return {
            'supports': supports,
            'contradicts': contradicts,
            'relevance': total_relevance,
            'confidence': total_confidence / max(len(data), 1)
        }
    
    def _extract_key_terms(self, claim: str) -> List[str]:
        """Extract key terms from a claim for searching"""
        # Simple keyword extraction - remove stop words and get important terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b\w+\b', claim.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return top 5 most frequent terms
        from collections import Counter
        word_counts = Counter(key_terms)
        return [word for word, _ in word_counts.most_common(5)]
    
    def _extract_claims_from_content(self, content: str) -> List[str]:
        """Extract factual claims from content"""
        if not content:
            return []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter for sentences that look like claims
        claims = []
        claim_patterns = [
            r'\b(is|are|was|were|has|have|can|will|should)\b',
            r'\baccording to\b',
            r'\bresearch shows\b',
            r'\bstudies indicate\b',
            r'\bdata suggests\b'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(re.search(pattern, sentence, re.IGNORECASE) for pattern in claim_patterns):
                claims.append(sentence)
        
        return claims[:10]  # Limit to 10 claims
    
    def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """Calculate similarity between two concepts"""
        words1 = set(concept1.lower().split())
        words2 = set(concept2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_content_relevance(self, node: ConceptNode, item: Dict[str, Any]) -> float:
        """Calculate relevance of external content to the node"""
        node_text = (node.concept + ' ' + node.content).lower()
        item_text = (
            item.get('title', '') + ' ' + 
            item.get('content', item.get('description', item.get('abstract', ''))
        ).lower()
        
        # Simple relevance based on word overlap
        node_words = set(node_text.split())
        item_words = set(item_text.split())
        
        if not node_words or not item_words:
            return 0.0
        
        intersection = node_words.intersection(item_words)
        return len(intersection) / len(node_words)
    
    def _calculate_node_reliability(self, node: ConceptNode, 
                                  cross_refs: List[Dict], 
                                  verified_claims: List[FactCheck]) -> float:
        """Calculate overall reliability score for a node"""
        factors = []
        
        # Factor 1: Cross-reference reliability
        if cross_refs:
            high_reliability_refs = len([
                ref for ref in cross_refs 
                if ref['source_reliability'] == ReliabilityScore.HIGH.value
            ])
            cross_ref_score = high_reliability_refs / len(cross_refs)
            factors.append(cross_ref_score)
        
        # Factor 2: Fact verification score
        if verified_claims:
            verified_count = len([
                fc for fc in verified_claims 
                if fc.status == FactStatus.VERIFIED
            ])
            fact_score = verified_count / len(verified_claims)
            factors.append(fact_score)
        
        # Factor 3: Source reliability of original content
        original_source = node.metadata.get('source_agent', 'unknown')
        if original_source in self.source_reliability:
            source_score = self.source_reliability[original_source].confidence
            factors.append(source_score)
        
        return sum(factors) / len(factors) if factors else 0.5
    
    def _find_contradictory_claims(self, claims1: List[str], claims2: List[str]) -> List[Tuple[str, str]]:
        """Find contradictory claim pairs"""
        contradictions = []
        contradict_patterns = [
            (r'\bnot\b', r'\b(is|are|was|were)\b'),
            (r'\bno\b', r'\b(yes|true|correct)\b'),
            (r'\bfalse\b', r'\b(true|correct)\b'),
            (r'\bincorrect\b', r'\b(correct|accurate)\b')
        ]
        
        for claim1 in claims1:
            for claim2 in claims2:
                claim1_lower = claim1.lower()
                claim2_lower = claim2.lower()
                
                for neg_pattern, pos_pattern in contradict_patterns:
                    if (re.search(neg_pattern, claim1_lower) and 
                        re.search(pos_pattern, claim2_lower)) or \
                       (re.search(neg_pattern, claim2_lower) and 
                        re.search(pos_pattern, claim1_lower)):
                        contradictions.append((claim1, claim2))
                        break
        
        return contradictions
    
    async def _discover_related_concepts(self, node: ConceptNode) -> List[Dict[str, Any]]:
        """Discover concepts related to a node through various sources"""
        related = []
        
        # Use existing edges as a starting point
        for edge in self.knowledge_graph.edges.values():
            if edge.source_node_id == node.id:
                target_node = self.knowledge_graph.nodes.get(edge.target_node_id)
                if target_node:
                    related.append({
                        'concept': target_node.concept,
                        'confidence': edge.weight,
                        'source': 'knowledge_graph'
                    })
        
        # Search for related concepts
        if len(related) < 5:  # Need more related concepts
            results = await self.data_pipeline.comprehensive_search(
                node.concept,
                sources=['wikipedia', 'academic']
            )
            
            for source, result in results.items():
                if result.success and result.data:
                    for item in result.data[:2]:  # Top 2 items
                        related.append({
                            'concept': item.get('title', ''),
                            'confidence': 0.7,
                            'source': source
                        })
        
        return related[:10]  # Limit to 10 related concepts