import { useState, useEffect, useRef, useCallback } from 'react';
import { conceptApi } from '../api';

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

  const fetchGraph = useCallback(async () => {
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
  }, [limit]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

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

  const fetchExploration = useCallback(async () => {
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
  }, [explorationId]);

  useEffect(() => {
    fetchExploration();
  }, [fetchExploration]);

  return { data, loading, error, refetch: fetchExploration };
};

// Custom hook for SSE real-time exploration events
export const useExplorationEvents = (explorationId) => {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [completed, setCompleted] = useState(false);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!explorationId) return;

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    const url = `${API_BASE_URL}/events/${explorationId}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.type === 'connected') {
          setConnected(true);
          return;
        }
        if (parsed.type === 'keepalive') {
          return;
        }
        setEvents((prev) => [...prev, parsed]);
        if (parsed.type === 'exploration_complete') {
          setCompleted(true);
          es.close();
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    es.onerror = () => {
      setConnected(false);
      es.close();
    };

    return () => {
      es.close();
    };
  }, [explorationId]);

  return { events, connected, completed };
};

// Custom hook for fetching explorations list
export const useExplorations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const fetchExplorations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await conceptApi.getExplorations();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExplorations();
  }, [fetchExplorations]);

  return { data, loading, error, refetch: fetchExplorations };
};
