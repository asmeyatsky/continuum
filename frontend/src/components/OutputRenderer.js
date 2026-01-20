import React, { useState } from 'react';
import styled from 'styled-components';
import { FiLayout, FiBook, FiPlay, FiEye, FiX } from 'react-icons/fi';
import ConceptCanvas3D from './ConceptCanvas3D';

const OutputContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 30px;
`;

const OutputHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const OutputTitle = styled.h2`
  font-size: 1.3rem;
  color: #495057;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const LayoutSelector = styled.div`
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  padding: 4px;
  border-radius: 8px;
`;

const LayoutButton = styled.button`
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: ${props => props.active ? '#667eea' : 'transparent'};
  color: ${props => props.active ? 'white' : '#6c757d'};
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: ${props => props.active ? '#5a6fd8' : '#e9ecef'};
  }
`;

const ContentSection = styled.div`
  display: ${props => props.visible ? 'block' : 'none'};
`;

const SectionHeader = styled.h3`
  font-size: 1.1rem;
  color: #495057;
  margin: 20px 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TextContent = styled.div`
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
`;

const MultimediaGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
`;

const MediaItem = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
`;

const MediaThumbnail = styled.div`
  height: 120px;
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 2rem;
`;

const MediaInfo = styled.div`
  padding: 12px;
`;

const MediaTitle = styled.div`
  font-weight: 500;
  color: #212529;
  margin-bottom: 4px;
  font-size: 0.9rem;
`;

const MediaDetails = styled.div`
  font-size: 0.8rem;
  color: #6c757d;
`;

const OutputRenderer = ({ explorationId }) => {
  const [layoutType, setLayoutType] = useState('adaptive');
  const [sections, setSections] = useState({
    knowledgeGraph: true,
    textExplanation: true,
    multimedia: true
  });

  // Mock data - in a real app this would come from the API
  const mockMultimedia = [
    { id: 'img_1', type: 'diagram', title: 'AI Concept Map', source: 'VisualAgent' },
    { id: 'video_1', type: 'video', title: 'Neural Networks Explained', duration: '5:30', source: 'MultimediaAgent' },
    { id: 'audio_1', type: 'audio', title: 'AI Ethics Overview', duration: '8:15', source: 'MultimediaAgent' }
  ];

  const mockTextContent = `# Exploration Results: ${explorationId}

## Summary
The system has identified key concepts related to this exploration, including primary themes, secondary connections, and emerging patterns.

## Key Findings
1. The concept demonstrates strong connections to foundational principles
2. Multiple interdisciplinary applications have been identified
3. Several unexpected relationships were discovered between related fields

## Detailed Analysis
The exploration revealed rich connections across multiple domains, suggesting a complex network of interrelated concepts that the system has mapped in the knowledge graph.

## Connections
The system identified 23 direct connections and 67 indirect relationships, with confidence scores ranging from 0.7 to 0.95.`;

  const toggleSection = (section) => {
    setSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const layoutTypes = [
    { key: 'adaptive', label: 'Adaptive', icon: <FiLayout /> },
    { key: 'reading', label: 'Reading', icon: <FiBook /> },
    { key: 'presentation', label: 'Presentation', icon: <FiPlay /> }
  ];

  return (
    <OutputContainer>
      <OutputHeader>
        <OutputTitle><FiEye /> Exploration Results</OutputTitle>
        <LayoutSelector>
          {layoutTypes.map(layout => (
            <LayoutButton
              key={layout.key}
              active={layoutType === layout.key}
              onClick={() => setLayoutType(layout.key)}
            >
              {layout.icon} {layout.label}
            </LayoutButton>
          ))}
        </LayoutSelector>
      </OutputHeader>

      {layoutType === 'adaptive' && (
        <>
          {sections.knowledgeGraph && (
            <ContentSection visible={true}>
              <SectionHeader>
                Knowledge Graph Visualization
                <button 
                  onClick={() => toggleSection('knowledgeGraph')}
                  style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  <FiX size={16} />
                </button>
              </SectionHeader>
              <ConceptCanvas3D />
            </ContentSection>
          )}

          {sections.textExplanation && (
            <ContentSection visible={true}>
              <SectionHeader>
                Comprehensive Explanation
                <button 
                  onClick={() => toggleSection('textExplanation')}
                  style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  <FiX size={16} />
                </button>
              </SectionHeader>
              <TextContent>{mockTextContent}</TextContent>
            </ContentSection>
          )}

          {sections.multimedia && (
            <ContentSection visible={true}>
              <SectionHeader>
                Generated Content
                <button 
                  onClick={() => toggleSection('multimedia')}
                  style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  <FiX size={16} />
                </button>
              </SectionHeader>
              <MultimediaGrid>
                {mockMultimedia.map(item => (
                  <MediaItem key={item.id}>
                    <MediaThumbnail>
                      {item.type === 'diagram' && '📊'}
                      {item.type === 'video' && '🎬'}
                      {item.type === 'audio' && '🎵'}
                    </MediaThumbnail>
                    <MediaInfo>
                      <MediaTitle>{item.title}</MediaTitle>
                      <MediaDetails>
                        {item.type} • {item.duration || 'N/A'} • {item.source}
                      </MediaDetails>
                    </MediaInfo>
                  </MediaItem>
                ))}
              </MultimediaGrid>
            </ContentSection>
          )}
        </>
      )}

      {layoutType === 'reading' && (
        <div>
          <SectionHeader>Reading View</SectionHeader>
          <TextContent>{mockTextContent}</TextContent>
        </div>
      )}

      {layoutType === 'presentation' && (
        <div>
          <SectionHeader>Presentation View</SectionHeader>
          <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <h3>Slide 1: Introduction</h3>
            <p>Exploring {explorationId} and related concepts</p>
            
            <h3 style={{ marginTop: '30px' }}>Slide 2: Key Concepts</h3>
            <p>Main ideas discovered during exploration</p>
            
            <h3 style={{ marginTop: '30px' }}>Slide 3: Connections</h3>
            <p>Relationships between concepts</p>
          </div>
        </div>
      )}
    </OutputContainer>
  );
};

export default OutputRenderer;