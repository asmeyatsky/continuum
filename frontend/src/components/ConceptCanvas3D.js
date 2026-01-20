import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import ForceGraph3D from 'react-force-graph-3d';
import { FiMaximize2, FiMinimize2, FiRefreshCw, FiDownload } from 'react-icons/fi';
import { useKnowledgeGraph } from '../utils/hooks';

const CanvasContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: 500px;
  position: relative;
`;

const CanvasHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const CanvasTitle = styled.h2`
  font-size: 1.1rem;
  color: #495057;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Controls = styled.div`
  display: flex;
  gap: 10px;
`;

const ControlButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #6c757d;
  
  &:hover {
    background: #e9ecef;
    color: #495057;
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
`;

const ConceptCanvas3D = () => {
  const { data, loading, error, refetch } = useKnowledgeGraph(50);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const fgRef = useRef();

  // Process API data to match ForceGraph format
  const graphData = {
    nodes: data?.nodes?.map(node => ({
      id: node.id,
      name: node.concept,
      group: node.metadata?.source_agent || 'unknown',
      val: node.metadata?.connections?.length || 1
    })) || [],
    links: data?.edges?.map(edge => ({
      source: edge.source,
      target: edge.target,
      name: edge.relationship_type
    })) || []
  };

  // Highlight nodes and links on hover
  const handleNodeHover = (node) => {
    highlightNodes.clear();
    highlightLinks.clear();

    if (node) {
      highlightNodes.add(node);
      // Add neighbors
      graphData.links
        .filter(link => link.source === node || link.target === node)
        .forEach(link => {
          highlightNodes.add(link.source);
          highlightNodes.add(link.target);
          highlightLinks.add(link);
        });
    }

    setHighlightNodes(new Set(highlightNodes));
    setHighlightLinks(new Set(highlightLinks));
  };

  if (loading && !graphData.nodes.length) {
    return (
      <CanvasContainer>
        <CanvasHeader>
          <CanvasTitle><FiMaximize2 /> Knowledge Graph Explorer</CanvasTitle>
          <Controls>
            <ControlButton onClick={refetch} title="Refresh"><FiRefreshCw /></ControlButton>
          </Controls>
        </CanvasHeader>
        <LoadingOverlay>
          <div>Loading knowledge graph...</div>
        </LoadingOverlay>
      </CanvasContainer>
    );
  }

  if (error) {
    return (
      <CanvasContainer>
        <CanvasHeader>
          <CanvasTitle><FiMaximize2 /> Knowledge Graph Explorer</CanvasTitle>
          <Controls>
            <ControlButton onClick={refetch} title="Refresh"><FiRefreshCw /></ControlButton>
          </Controls>
        </CanvasHeader>
        <div>Error loading knowledge graph: {error.message}</div>
      </CanvasContainer>
    );
  }

  return (
    <CanvasContainer>
      <CanvasHeader>
        <CanvasTitle><FiMaximize2 /> Knowledge Graph Explorer</CanvasTitle>
        <Controls>
          <ControlButton onClick={refetch} title="Refresh"><FiRefreshCw /></ControlButton>
          <ControlButton title="Zoom out"><FiMinimize2 /></ControlButton>
          <ControlButton title="Download"><FiDownload /></ControlButton>
        </Controls>
      </CanvasHeader>
      <ForceGraph3D
        ref={fgRef}
        graphData={graphData}
        nodeLabel={node => `${node.name}`}
        nodeAutoColorBy="group"
        nodeVal={node => Math.sqrt(node.val || 1) * 5}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        linkLabel={link => link.name}
        backgroundColor="#f8f9fa"
        width={600}
        height={400}
        onNodeHover={handleNodeHover}
        linkColor={link => highlightLinks.has(link) ? '#667eea' : '#e9ecef'}
        nodeColor={node => highlightNodes.has(node) ? '#667eea' : '#764ba2'}
        nodeOpacity={0.9}
        nodeResolution={16}
      />
    </CanvasContainer>
  );
};

export default ConceptCanvas3D;