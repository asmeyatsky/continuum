# Continuum Frontend

This is the React frontend for the Infinite Concept Expansion Engine (Continuum). It provides a modern, interactive interface for exploring concepts and visualizing knowledge graphs.

## Features

- **Dashboard**: Real-time metrics and exploration status
- **Knowledge Graph Visualization**: Interactive 3D visualization of concept relationships
- **Concept Explorer**: Interface for submitting new concepts to explore
- **Live Feed**: Real-time updates on ongoing expansions
- **Media Gallery**: Display of generated multimedia content
- **Multiple Layouts**: Adaptive, reading, and presentation modes

## Installation

1. Make sure you have Node.js (>=14.0.0) and npm installed
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Create a `.env` file in the frontend directory with the following content:
   ```env
   REACT_APP_API_URL=http://localhost:8000/api
   ```
5. Start the development server:
   ```bash
   npm start
   ```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Runs tests
- `npm run eject` - Ejects from Create React App (irreversible)

## API Integration

The frontend connects to the Continuum backend API running on `http://localhost:8000/api` by default. Make sure the backend server is running before starting the frontend.

## Architecture

- **Components**: Reusable UI elements
- **Containers**: Page-level components that manage data
- **API**: Service layer for backend communication
- **Utils**: Helper functions and custom hooks
- **Styles**: Global styles and component-specific styling

## Dependencies

- React 18
- React Router for navigation
- Styled Components for styling
- Recharts for data visualization
- React Force Graph for 3D knowledge graph visualization
- Axios for API communication