import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { FiActivity, FiGrid, FiZap, FiClock, FiTrendingUp } from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import MetricsCard from '../components/MetricsCard';
import ConceptCanvas3D from '../components/ConceptCanvas3D';
import LiveFeed from '../components/LiveFeed';
import MediaGallery from '../components/MediaGallery';
import OutputRenderer from '../components/OutputRenderer';
import { conceptApi } from '../api';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 2rem;
  color: #212529;
  font-weight: 700;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const ChartSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
`;

const SectionTitle = styled.h2`
  font-size: 1.2rem;
  color: #495057;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    active_explorations: 0,
    total_nodes: 0,
    total_edges: 0,
    total_explorations: 0,
  });
  const [recentEvents, setRecentEvents] = useState([]);

  const [expansionData] = useState([
    { day: 'Mon', expansions: 45 },
    { day: 'Tue', expansions: 52 },
    { day: 'Wed', expansions: 48 },
    { day: 'Thu', expansions: 61 },
    { day: 'Fri', expansions: 55 },
    { day: 'Sat', expansions: 49 },
    { day: 'Sun', expansions: 41 }
  ]);

  const fetchMetrics = useCallback(async () => {
    try {
      const [health, graph] = await Promise.all([
        conceptApi.healthCheck(),
        conceptApi.getKnowledgeGraph(100),
      ]);

      const engineData = health.engine || {};
      setMetrics({
        active_explorations: engineData.active_explorations || 0,
        total_nodes: engineData.total_nodes || graph?.total_nodes || 0,
        total_edges: engineData.total_edges || graph?.total_edges || 0,
        total_explorations: engineData.total_explorations || 0,
      });

      // Build recent events from graph nodes for the live feed
      if (graph?.nodes?.length) {
        const events = graph.nodes.slice(0, 10).map((node, i) => ({
          id: node.id,
          type: 'node',
          title: 'Concept node discovered',
          description: `"${node.concept}" added to knowledge graph`,
          source: node.metadata?.source_agent || 'System',
          time: node.created_at,
        }));
        setRecentEvents(events);
      }
    } catch (err) {
      // Backend may not be running yet — keep defaults
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  return (
    <DashboardContainer>
      <Header>
        <Title>Continuum Dashboard</Title>
      </Header>

      <StatsGrid>
        <MetricsCard
          icon={<FiActivity />}
          title="Active Explorations"
          value={metrics.active_explorations}
          change={`${metrics.total_explorations} total`}
          color="#667eea"
        />
        <MetricsCard
          icon={<FiGrid />}
          title="Knowledge Nodes"
          value={metrics.total_nodes}
          change={`${metrics.total_edges} connections`}
          color="#764ba2"
        />
        <MetricsCard
          icon={<FiZap />}
          title="Connections"
          value={metrics.total_edges}
          change="edges in graph"
          color="#f093fb"
        />
        <MetricsCard
          icon={<FiClock />}
          title="Explorations"
          value={metrics.total_explorations}
          change="total runs"
          color="#4facfe"
        />
      </StatsGrid>

      <ChartSection>
        <SectionTitle><FiTrendingUp /> Expansion Activity</SectionTitle>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={expansionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="expansions" stroke="#667eea" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartSection>

      <ChartSection>
        <SectionTitle><FiGrid /> Concept Connections</SectionTitle>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={expansionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="expansions" fill="#764ba2" />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px', marginBottom: '30px' }}>
        <ConceptCanvas3D />
        <div>
          <LiveFeed events={recentEvents} />
          <MediaGallery />
        </div>
      </div>

      <OutputRenderer explorationId="dashboard-view" />
    </DashboardContainer>
  );
};

export default Dashboard;
