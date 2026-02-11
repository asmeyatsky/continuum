import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { FiArrowLeft, FiActivity, FiGrid, FiZap, FiCheckCircle, FiLoader } from 'react-icons/fi';
import { conceptApi } from '../api';
import { useExplorationEvents } from '../utils/hooks';
import ConceptCanvas3D from '../components/ConceptCanvas3D';
import LiveFeed from '../components/LiveFeed';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
`;

const BackLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 6px;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;

  &:hover {
    opacity: 0.8;
  }
`;

const Title = styled.h1`
  font-size: 1.8rem;
  color: #212529;
  font-weight: 700;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;

  ${props => props.$status === 'processing' || props.$status === 'in_progress' ? `
    background: #fff3cd;
    color: #856404;
  ` : props.$status === 'completed' ? `
    background: #d4edda;
    color: #155724;
  ` : `
    background: #e2e3e5;
    color: #383d41;
  `}
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.color || '#212529'};
`;

const StatLabel = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 4px;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const NodeList = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 20px;
`;

const NodeListTitle = styled.h3`
  font-size: 1rem;
  color: #495057;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const NodeItem = styled.div`
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const NodeConcept = styled.div`
  font-weight: 500;
  color: #212529;
  margin-bottom: 4px;
`;

const NodeAgent = styled.span`
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  background: #e8eafd;
  color: #667eea;
  margin-right: 6px;
`;

const NodeContent = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 6px;
  line-height: 1.4;
  max-height: 80px;
  overflow: hidden;
`;

function extractSummary(content) {
  if (!content) return '';
  // Try to extract a readable summary from the stringified dict
  const summaryMatch = content.match(/'summary':\s*'([^']+)'/);
  if (summaryMatch) return summaryMatch[1];
  const explMatch = content.match(/'explanation':\s*'([^']+)'/);
  if (explMatch) return explMatch[1];
  const descMatch = content.match(/'description':\s*'([^']+)'/);
  if (descMatch) return descMatch[1];
  // Fallback: show truncated content
  const clean = content.replace(/[{}']/g, '').substring(0, 150);
  return clean + (content.length > 150 ? '...' : '');
}

const ExplorationResults = () => {
  const { explorationId } = useParams();
  const [exploration, setExploration] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const { events, completed: sseCompleted } = useExplorationEvents(explorationId);

  const fetchData = useCallback(async () => {
    if (!explorationId) return;
    try {
      const [expData, nodesData] = await Promise.all([
        conceptApi.getExploration(explorationId),
        conceptApi.getExplorationNodes(explorationId),
      ]);
      setExploration(expData);
      setNodes(nodesData.nodes || []);
    } catch (err) {
      console.error('Error fetching exploration data:', err);
    } finally {
      setLoading(false);
    }
  }, [explorationId]);

  // Initial fetch + poll while processing
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Stop polling once completed
  const status = sseCompleted ? 'completed' : (exploration?.status || 'processing');
  const isProcessing = status === 'processing' || status === 'in_progress';

  // Build live feed items from fetched nodes
  const feedItems = nodes.slice(0, 15).map((node) => ({
    id: node.id,
    type: 'node',
    title: `Discovered by ${node.metadata?.source_agent || 'agent'}`,
    description: node.concept,
    time: node.created_at,
  }));

  // Group nodes by agent for a summary view
  const agentGroups = {};
  nodes.forEach((node) => {
    const agent = node.metadata?.source_agent || 'Unknown';
    if (!agentGroups[agent]) agentGroups[agent] = [];
    agentGroups[agent].push(node);
  });

  if (loading && !exploration) {
    return (
      <Container>
        <Header>
          <BackLink to="/explore"><FiArrowLeft /> Back to Explorer</BackLink>
        </Header>
        <div>Loading exploration...</div>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <BackLink to="/explore"><FiArrowLeft /> Back to Explorer</BackLink>
      </Header>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '25px' }}>
        <Title>{exploration?.concept || 'Exploration'}</Title>
        <StatusBadge $status={status}>
          {isProcessing ? <FiLoader /> : <FiCheckCircle />}
          {isProcessing ? 'Processing...' : 'Completed'}
        </StatusBadge>
      </div>

      <StatsGrid>
        <StatCard>
          <StatValue color="#667eea">{exploration?.nodes_count || nodes.length}</StatValue>
          <StatLabel>Nodes Discovered</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#764ba2">{Object.keys(agentGroups).length}</StatValue>
          <StatLabel>Agents Used</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#f093fb">{events.length}</StatValue>
          <StatLabel>Live Events</StatLabel>
        </StatCard>
      </StatsGrid>

      <ContentGrid>
        <ConceptCanvas3D refreshInterval={isProcessing ? 3000 : undefined} />
        <div>
          <LiveFeed events={feedItems} />
        </div>
      </ContentGrid>

      {Object.entries(agentGroups).map(([agent, agentNodes]) => (
        <NodeList key={agent}>
          <NodeListTitle><FiGrid /> {agent} ({agentNodes.length} results)</NodeListTitle>
          {agentNodes.map((node) => (
            <NodeItem key={node.id}>
              <NodeConcept>
                <NodeAgent>{agent}</NodeAgent>
                {node.concept}
              </NodeConcept>
              <NodeContent>{extractSummary(node.content)}</NodeContent>
            </NodeItem>
          ))}
        </NodeList>
      ))}
    </Container>
  );
};

export default ExplorationResults;
