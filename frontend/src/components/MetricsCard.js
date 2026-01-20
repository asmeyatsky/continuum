import React from 'react';
import styled from 'styled-components';

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const IconContainer = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.color}20;
  color: ${props => props.color};
`;

const Title = styled.h3`
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
`;

const Value = styled.div`
  font-size: 1.8rem;
  font-weight: 700;
  color: #212529;
`;

const Change = styled.div`
  font-size: 0.8rem;
  color: #28a745;
  font-weight: 500;
`;

const MetricsCard = ({ icon, title, value, change, color }) => {
  return (
    <Card>
      <Header>
        <div>
          <Title>{title}</Title>
          <Value>{value}</Value>
        </div>
        <IconContainer color={color}>
          {icon}
        </IconContainer>
      </Header>
      <Change>{change}</Change>
    </Card>
  );
};

export default MetricsCard;