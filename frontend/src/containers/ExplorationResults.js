import React from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { FiArrowLeft, FiActivity, FiGrid, FiZap, FiCheckCircle, FiLoader } from 'react-icons/fi';
import { useExploration, useExplorationEvents } from '../utils/hooks';
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

  ${props => props.status === 'processing' || props.status === 'in_progress' ? `
    background: #fff3cd;
    color: #856404;
  ` : props.status === 'completed' ? `
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
  padding: 10px 0;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const NodeConcept = styled.div`
  font-weight: 500;
  color: #212529;
`;

const NodeMeta = styled.div`
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 2px;
`;

const ExplorationResults = () => {
  const { explorationId } = useParams();
  const { data: exploration, loading } = useExploration(explorationId);
  const { events, completed } = useExplorationEvents(explorationId);

  // Derive status from exploration data or SSE
  const status = completed ? 'completed' : (exploration?.status || 'processing');

  // Build feed items from SSE events
  const feedItems = events
    .filter(e => e.type === 'node_created' || e.type === 'expansion_cycle_complete')
    .map((e, i) => {
      if (e.type === 'node_created') {
        return {
          id: `event-${i}`,
          type: 'node',
          title: 'New concept discovered',
          description: `"${e.data?.concept}" by ${e.data?.source_agent || 'agent'}`,
          time: e.data?.timestamp,
        };
      }
      return {
        id: `event-${i}`,
        type: 'content',
        title: 'Expansion cycle complete',
        description: `${e.data?.successful_agents || 0} agents succeeded - ${e.data?.total_nodes || 0} total nodes`,
        time: e.data?.timestamp,
      };
    });

  // Count nodes from events
  const nodesFromEvents = events.filter(e => e.type === 'node_created').length;
  const displayNodes = exploration?.nodes_count
    ? Math.max(exploration.nodes_count, nodesFromEvents)
    : nodesFromEvents;
  const displayEdges = exploration?.connections_count || 0;

  // Node list from events
  const discoveredNodes = events
    .filter(e => e.type === 'node_created')
    .map(e => e.data);

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
        <StatusBadge status={status}>
          {status === 'completed' ? <FiCheckCircle /> : <FiLoader />}
          {status === 'in_progress' ? 'Processing' : status.charAt(0).toUpperCase() + status.slice(1)}
        </StatusBadge>
      </div>

      <StatsGrid>
        <StatCard>
          <StatValue color="#667eea"><FiGrid style={{ marginRight: 8 }} />{displayNodes}</StatValue>
          <StatLabel>Nodes Discovered</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#764ba2"><FiZap style={{ marginRight: 8 }} />{displayEdges}</StatValue>
          <StatLabel>Connections</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#f093fb"><FiActivity style={{ marginRight: 8 }} />{events.length}</StatValue>
          <StatLabel>Events</StatLabel>
        </StatCard>
      </StatsGrid>

      <ContentGrid>
        <ConceptCanvas3D refreshInterval={status !== 'completed' ? 3000 : undefined} />
        <div>
          <LiveFeed events={feedItems} />
          {discoveredNodes.length > 0 && (
            <NodeList>
              <NodeListTitle><FiGrid /> Discovered Concepts</NodeListTitle>
              {discoveredNodes.map((node, i) => (
                <NodeItem key={node.node_id || i}>
                  <NodeConcept>{node.concept}</NodeConcept>
                  <NodeMeta>by {node.source_agent} - confidence: {(node.confidence * 100).toFixed(0)}%</NodeMeta>
                </NodeItem>
              ))}
            </NodeList>
          )}
        </div>
      </ContentGrid>
    </Container>
  );
};

export default ExplorationResults;
