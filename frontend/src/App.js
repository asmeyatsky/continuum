import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Dashboard from './containers/Dashboard';
import ConceptExplorer from './containers/ConceptExplorer';
import Navigation from './components/Navigation';
import GlobalStyle from './styles/GlobalStyle';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 20px;
  margin-top: 60px;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <GlobalStyle />
        <Navigation />
        <MainContent>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/explore" element={<ConceptExplorer />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </MainContent>
      </AppContainer>
    </Router>
  );
}

export default App;