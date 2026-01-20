import { useState, useEffect } from 'react';
import { conceptApi } from './api';

// Custom hook for submitting concepts
export const useSubmitConcept = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const submit = async (concept, context = '') => {
    setLoading(true);
    setError(null);
    try {
      const result = await conceptApi.submitConcept(concept, context);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { submit, loading, error, data };
};

// Custom hook for fetching knowledge graph
export const useKnowledgeGraph = (limit = 100) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await conceptApi.getKnowledgeGraph(limit);
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, [limit]);

  return { data, loading, error, refetch: fetchGraph };
};

// Custom hook for searching
export const useSearchGraph = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const search = async (query, limit = 10) => {
    setLoading(true);
    setError(null);
    try {
      const result = await conceptApi.searchGraph(query, limit);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { search, loading, error, data };
};

// Custom hook for exploration status
export const useExploration = (explorationId) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const fetchExploration = async () => {
    if (!explorationId) return;
    
    setLoading(true);
    setError(null);
    try {
      const result = await conceptApi.getExploration(explorationId);
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExploration();
  }, [explorationId]);

  return { data, loading, error, refetch: fetchExploration };
};