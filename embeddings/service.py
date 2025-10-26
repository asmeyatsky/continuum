"""
Embedding service for semantic search and similarity computation.

Uses Sentence Transformers for high-quality embeddings.
"""
import logging
from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing embeddings.

    Uses Sentence Transformers for semantic understanding.
    Falls back to simple embeddings when sentence-transformers is not available.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize embedding service.

        Args:
            model_name: Name of the Sentence Transformer model to use
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.embedding_dim = settings.EMBEDDING_DIM
        self.use_sentence_transformers = False

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.use_sentence_transformers = True
            logger.info(f"Embedding model loaded: {self.model_name}")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embedding service. "
                "Install with: pip install sentence-transformers"
            )
            self.model = None
            self.use_sentence_transformers = False
        except Exception as e:
            logger.warning(f"Error loading embedding model: {e}. Using fallback embedding service.")
            self.model = None
            self.use_sentence_transformers = False

    def encode(self, text: str) -> np.ndarray:
        """
        Encode text into an embedding vector.

        Args:
            text: Text to encode

        Returns:
            Embedding vector as numpy array
        """
        try:
            if self.use_sentence_transformers and self.model:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.astype(np.float32)
            else:
                # Fallback: Simple character frequency based embedding
                return self._generate_fallback_embedding(text)
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            # Use fallback on error
            return self._generate_fallback_embedding(text)

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts into embedding vectors.

        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing

        Returns:
            Matrix of embedding vectors (n_samples, embedding_dim)
        """
        try:
            if self.use_sentence_transformers and self.model:
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                )
                return embeddings.astype(np.float32)
            else:
                # Fallback: Generate embeddings one by one using fallback method
                embeddings = []
                for text in texts:
                    embeddings.append(self._generate_fallback_embedding(text))
                return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"Error batch encoding texts: {e}")
            # Use fallback on error
            embeddings = []
            for text in texts:
                embeddings.append(self._generate_fallback_embedding(text))
            return np.array(embeddings, dtype=np.float32)

    def similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Ensure embeddings are 2D for cosine_similarity
            emb1 = embedding1.reshape(1, -1) if embedding1.ndim == 1 else embedding1
            emb2 = embedding2.reshape(1, -1) if embedding2.ndim == 1 else embedding2

            sim = cosine_similarity(emb1, emb2)[0, 0]
            return float(sim)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def find_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Matrix of candidate embeddings
            top_k: Number of top results to return
            threshold: Minimum similarity threshold

        Returns:
            List of (index, similarity) tuples sorted by similarity
        """
        try:
            query = (
                query_embedding.reshape(1, -1)
                if query_embedding.ndim == 1
                else query_embedding
            )

            similarities = cosine_similarity(query, candidate_embeddings)[0]

            # Filter by threshold
            valid_indices = np.where(similarities >= threshold)[0]
            valid_similarities = similarities[valid_indices]

            # Sort by similarity descending
            sorted_idx = np.argsort(-valid_similarities)[:top_k]
            results = [
                (int(valid_indices[i]), float(valid_similarities[i]))
                for i in sorted_idx
            ]

            return results
        except Exception as e:
            logger.error(f"Error finding similar embeddings: {e}")
            return []

    def semantic_search(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[tuple[int, float]]:
        """
        Perform semantic search to find similar candidates to a query.

        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return

        Returns:
            List of (candidate_index, similarity_score) tuples
        """
        try:
            # Encode query and candidates
            query_emb = self.encode(query)
            candidate_embs = self.encode_batch(candidates)

            # Find similar
            results = self.find_similar(query_emb, candidate_embs, top_k=top_k)
            return results
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []

    def _generate_fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate a fallback embedding for the text.

        Used when Sentence Transformers is not available.
        This is a basic character-frequency based embedding.
        """
        # Create an embedding with the configured dimension
        embedding = np.zeros(self.embedding_dim, dtype=np.float32)

        if not text:
            return embedding

        # Simple character frequency encoding
        char_freq = {}
        for char in text.lower():
            if char.isalnum():  # Only alphanumeric characters
                char_freq[char] = char_freq.get(char, 0) + 1

        # Map character frequencies to embedding dimensions
        if char_freq:
            max_freq = max(char_freq.values()) if char_freq.values() else 1
            chars = sorted(char_freq.keys())
            for i, char in enumerate(chars):
                if i < len(embedding):
                    embedding[i] = char_freq[char] / max_freq

        # Add text length encoding in later positions
        text_length = len(text)
        start_idx = min(len(embedding) // 4, len(embedding) - 1)
        end_idx = min(start_idx + 10, len(embedding))
        for i in range(start_idx, end_idx):
            embedding[i] = min(text_length / 1000, 1.0)

        return embedding.astype(np.float32)
