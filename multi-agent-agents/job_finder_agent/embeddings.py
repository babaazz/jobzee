import numpy as np
from typing import List, Dict, Any
import openai
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", openai_api_key: str = None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.openai_api_key = openai_api_key
        
        if openai_api_key:
            openai.api_key = openai_api_key
            
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
            
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
            
    def generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided")
            
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            raise
            
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise
            
    def find_similar_jobs(self, query_embedding: List[float], job_embeddings: List[Dict[str, Any]], 
                         min_score: float = 0.7, max_results: int = 10) -> List[Dict[str, Any]]:
        """Find similar jobs based on embedding similarity"""
        try:
            similarities = []
            
            for job in job_embeddings:
                if 'embedding' in job:
                    similarity = self.calculate_similarity(query_embedding, job['embedding'])
                    if similarity >= min_score:
                        similarities.append({
                            'job': job,
                            'similarity': similarity
                        })
                        
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top results
            return similarities[:max_results]
        except Exception as e:
            logger.error(f"Error finding similar jobs: {e}")
            raise 