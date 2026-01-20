import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const conceptApi = {
  // Submit a concept for exploration
  submitConcept: async (concept, context = '') => {
    const response = await apiClient.post('/explore', { concept, context });
    return response.data;
  },

  // Get exploration by ID
  getExploration: async (explorationId) => {
    const response = await apiClient.get(`/explorations/${explorationId}`);
    return response.data;
  },

  // Get all explorations
  getExplorations: async () => {
    const response = await apiClient.get('/explorations');
    return response.data;
  },

  // Get graph data for an exploration
  getGraph: async (explorationId) => {
    const response = await apiClient.get(`/graph/${explorationId}`);
    return response.data;
  },

  // Submit feedback
  submitFeedback: async (explorationId, feedback) => {
    const response = await apiClient.post(`/feedback/${explorationId}`, feedback);
    return response.data;
  },

  // Get generated content
  getContent: async (explorationId) => {
    const response = await apiClient.get(`/content/${explorationId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
