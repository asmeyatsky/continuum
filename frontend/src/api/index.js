import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('continuum_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('continuum_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const conceptApi = {
  // Submit a concept for expansion
  submitConcept: async (concept, context = '') => {
    try {
      const response = await apiClient.post('/concepts/expand', {
        concept,
        context,
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting concept:', error);
      throw error;
    }
  },

  // Get exploration status
  getExploration: async (explorationId) => {
    try {
      const response = await apiClient.get(`/concepts/${explorationId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting exploration:', error);
      throw error;
    }
  },

  // Get knowledge graph
  getKnowledgeGraph: async (limit = 100) => {
    try {
      const response = await apiClient.get('/graph', { params: { limit } });
      return response.data;
    } catch (error) {
      console.error('Error getting knowledge graph:', error);
      throw error;
    }
  },

  // Get a specific node
  getNode: async (nodeId) => {
    try {
      const response = await apiClient.get(`/nodes/${nodeId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting node:', error);
      throw error;
    }
  },

  // Search the knowledge graph
  searchGraph: async (query, limit = 10) => {
    try {
      const response = await apiClient.post('/search', {
        query,
        limit,
      });
      return response.data;
    } catch (error) {
      console.error('Error searching graph:', error);
      throw error;
    }
  },

  // Submit feedback
  submitFeedback: async (explorationId, rating, comment = '') => {
    try {
      const response = await apiClient.post('/feedback', {
        exploration_id: explorationId,
        rating,
        comment,
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },
};

export default apiClient;