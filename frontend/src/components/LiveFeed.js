import React from 'react';
import styled from 'styled-components';
import { FiActivity, FiImage, FiBook } from 'react-icons/fi';

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

const EmptyState = styled.div`
  text-align: center;
  padding: 20px;
  color: #adb5bd;
  font-size: 0.9rem;
`;

function formatRelativeTime(timestamp) {
  if (!timestamp) return '';
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return 'just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} min${diffMin > 1 ? 's' : ''} ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr} hr${diffHr > 1 ? 's' : ''} ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
}

const getIcon = (type) => {
  switch (type) {
    case 'node': return <FiActivity />;
    case 'content': return <FiImage />;
    case 'research': return <FiBook />;
    default: return <FiActivity />;
  }
};

const LiveFeed = ({ events }) => {
  const items = events && events.length > 0 ? events : null;

  return (
    <FeedContainer>
      <FeedHeader><FiActivity /> Live Expansion Feed</FeedHeader>
      {items ? (
        items.map(item => (
          <FeedItem key={item.id}>
            <IconWrapper type={item.type || 'node'}>
              {getIcon(item.type || 'node')}
            </IconWrapper>
            <FeedContent>
              <FeedTitle>{item.title}</FeedTitle>
              <FeedDescription>{item.description}</FeedDescription>
              <FeedTime>{typeof item.time === 'string' && item.time.includes('ago') ? item.time : formatRelativeTime(item.time)}</FeedTime>
            </FeedContent>
          </FeedItem>
        ))
      ) : (
        <EmptyState>No recent activity</EmptyState>
      )}
    </FeedContainer>
  );
};

export default LiveFeed;
