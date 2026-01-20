import React from 'react';
import styled from 'styled-components';
import { FiActivity, FiImage, FiVideo, FiBook } from 'react-icons/fi';

const FeedContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 20px;
`;

const FeedHeader = styled.h3`
  font-size: 1rem;
  color: #495057;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FeedItem = styled.div`
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;
  display: flex;
  gap: 12px;
  
  &:last-child {
    border-bottom: none;
  }
`;

const IconWrapper = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: ${props => {
    if (props.type === 'node') return '#d1ecf1';
    if (props.type === 'content') return '#d4edda';
    if (props.type === 'research') return '#f8d7da';
    return '#d1ecf1';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => {
    if (props.type === 'node') return '#0c5460';
    if (props.type === 'content') return '#155724';
    if (props.type === 'research') return '#721c24';
    return '#0c5460';
  }};
`;

const FeedContent = styled.div`
  flex: 1;
`;

const FeedTitle = styled.div`
  font-weight: 500;
  color: #212529;
  margin-bottom: 4px;
`;

const FeedDescription = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
`;

const FeedTime = styled.div`
  font-size: 0.75rem;
  color: #adb5bd;
`;

const LiveFeed = () => {
  const feedItems = [
    {
      id: 1,
      type: 'node',
      title: 'New concept node created',
      description: 'New concept node "Natural Language Processing" added to graph',
      source: 'ConnectionAgent',
      time: '2 mins ago'
    },
    {
      id: 2,
      type: 'content',
      title: 'Content generated',
      description: 'Generated multimedia content for "Computer Vision"',
      source: 'MultimediaAgent',
      time: '5 mins ago'
    },
    {
      id: 3,
      type: 'research',
      title: 'Research completed',
      description: 'Research on "Reinforcement Learning" completed with 5 sources',
      source: 'ResearchAgent',
      time: '8 mins ago'
    },
    {
      id: 4,
      type: 'node',
      title: 'Connection discovered',
      description: 'Discovered link between "Quantum Computing" and "Machine Learning"',
      source: 'ConnectionAgent',
      time: '12 mins ago'
    }
  ];

  const getIcon = (type) => {
    switch (type) {
      case 'node': return <FiActivity />;
      case 'content': return <FiImage />;
      case 'research': return <FiBook />;
      default: return <FiActivity />;
    }
  };

  return (
    <FeedContainer>
      <FeedHeader><FiActivity /> Live Expansion Feed</FeedHeader>
      {feedItems.map(item => (
        <FeedItem key={item.id}>
          <IconWrapper type={item.type}>
            {getIcon(item.type)}
          </IconWrapper>
          <FeedContent>
            <FeedTitle>{item.title}</FeedTitle>
            <FeedDescription>{item.description}</FeedDescription>
            <FeedTime>{item.time}</FeedTime>
          </FeedContent>
        </FeedItem>
      ))}
    </FeedContainer>
  );
};

export default LiveFeed;