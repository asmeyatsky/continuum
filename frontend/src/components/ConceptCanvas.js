import React from 'react';
import styled from 'styled-components';
import ForceGraph2D from 'react-force-graph-2d';
import { FiMaximize2, FiMinimize2, FiRefreshCw } from 'react-icons/fi';

const CanvasContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: 500px;
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

const ConceptCanvas = () => {
  // Sample data based on the existing UI components
  const nodes = [
    { id: "1", label: "AI Research", x: 0, y: 0 },
    { id: "2", label: "Machine Learning", x: 100, y: 50 },
    { id: "3", label: "Neural Networks", x: 200, y: 100 },
    { id: "4", label: "Deep Learning", x: 300, y: 150 },
    { id: "5", label: "NLP", x: 150, y: 200 },
    { id: "6", label: "Computer Vision", x: 250, y: 50 }
  ];

  const links = [
    { source: "1", target: "2" },
    { source: "2", target: "3" },
    { source: "3", target: "4" },
    { source: "2", target: "5" },
    { source: "2", target: "6" }
  ];

  return (
    <CanvasContainer>
      <CanvasHeader>
        <CanvasTitle><FiMaximize2 /> Concept Canvas</CanvasTitle>
        <Controls>
          <ControlButton><FiRefreshCw /></ControlButton>
          <ControlButton><FiMinimize2 /></ControlButton>
        </Controls>
      </CanvasHeader>
      <ForceGraph2D
        graphData={{ nodes, links }}
        nodeAutoColorBy="group"
        nodeLabel="label"
        linkDirectionalParticles={1}
        linkDirectionalParticleSpeed={0.003}
        linkLabel="type"
        backgroundColor="#f8f9fa"
        width={600}
        height={400}
        onNodeClick={node => console.log(node)}
      />
    </CanvasContainer>
  );
};

export default ConceptCanvas;