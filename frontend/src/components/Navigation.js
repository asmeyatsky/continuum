import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { FiHome, FiCompass, FiBarChart2, FiSettings } from 'react-icons/fi';

const Nav = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const Logo = styled(Link)`
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const NavLinks = styled.div`
  display: flex;
  margin-left: 40px;
  gap: 30px;
`;

const NavLink = styled(Link)`
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  
  &:hover {
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  &.active {
    color: white;
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

const Navigation = () => {
  return (
    <Nav>
      <Logo to="/">
        <FiCompass size={24} />
        Continuum
      </Logo>
      <NavLinks>
        <NavLink to="/" activeClassName="active">Dashboard</NavLink>
        <NavLink to="/explore" activeClassName="active">Explore</NavLink>
        <NavLink to="/dashboard" activeClassName="active">Analytics</NavLink>
      </NavLinks>
    </Nav>
  );
};

export default Navigation;