"""
Vector Database Client

This module provides a client for interacting with Qdrant vector database
for storing and searching candidate profiles and job postings.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import json
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct, Filter, FieldCondition,
        MatchValue, Range, SearchRequest
    )
    from qdrant_client.http import models
except ImportError:
    logging.warning("Qdrant client not available. Install with: pip install qdrant-client")
    QdrantClient = None

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from vector database."""
    
    document_id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    payload: Dict[str, Any] = None


@dataclass
class Document:
    """Represents a document in the vector database."""
    
    document_id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class VectorDatabase:
    """Client for interacting with Qdrant vector database."""
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 collection_prefix: str = "jobzee", dimension: int = 1536):
        self.host = host
        self.port = port
        self.collection_prefix = collection_prefix
        self.dimension = dimension
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Qdrant client."""
        try:
            if QdrantClient is None:
                raise ImportError("Qdrant client not available")
            
            self.client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self.client = None
    
    def _get_collection_name(self, base_name: str) -> str:
        """Get full collection name with prefix."""
        return f"{self.collection_prefix}_{base_name}"
    
    async def create_collection(self, collection_name: str, dimension: int = None) -> bool:
        """Create a new collection in the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return False
            
            full_name = self._get_collection_name(collection_name)
            dim = dimension or self.dimension
            
            # Check if collection already exists
            collections = self.client.get_collections()
            if any(col.name == full_name for col in collections.collections):
                logger.info(f"Collection {full_name} already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=full_name,
                vectors_config=VectorParams(
                    size=dim,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created collection: {full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    async def add_document(self, collection_name: str, document_id: str, 
                          text: str, metadata: Dict[str, Any] = None, 
                          embedding: List[float] = None) -> bool:
        """Add a document to the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return False
            
            full_name = self._get_collection_name(collection_name)
            
            # Ensure collection exists
            await self.create_collection(collection_name)
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "text": text,
                "document_id": document_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create point
            point = PointStruct(
                id=document_id,
                vector=embedding or [0.0] * self.dimension,  # Placeholder embedding
                payload=doc_metadata
            )
            
            # Add to collection
            self.client.upsert(
                collection_name=full_name,
                points=[point]
            )
            
            logger.info(f"Added document {document_id} to collection {full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {e}")
            return False
    
    async def get_document(self, collection_name: str, document_id: str) -> Optional[Document]:
        """Retrieve a document from the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return None
            
            full_name = self._get_collection_name(collection_name)
            
            # Retrieve point
            points = self.client.retrieve(
                collection_name=full_name,
                ids=[document_id]
            )
            
            if not points:
                logger.warning(f"Document {document_id} not found in collection {full_name}")
                return None
            
            point = points[0]
            
            # Create document object
            document = Document(
                document_id=point.id,
                text=point.payload.get("text", ""),
                metadata=point.payload,
                embedding=point.vector if hasattr(point, 'vector') else None,
                timestamp=datetime.fromisoformat(point.payload.get("timestamp", datetime.utcnow().isoformat()))
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
    
    async def search(self, collection_name: str, query: str, limit: int = 10,
                    filter_criteria: Dict[str, Any] = None) -> List[SearchResult]:
        """Search for documents in the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return []
            
            full_name = self._get_collection_name(collection_name)
            
            # Create search filter
            search_filter = None
            if filter_criteria:
                conditions = []
                for key, value in filter_criteria.items():
                    if isinstance(value, bool):
                        conditions.append(
                            FieldCondition(
                                key=key,
                                match=MatchValue(value=value)
                            )
                        )
                    elif isinstance(value, str):
                        conditions.append(
                            FieldCondition(
                                key=key,
                                match=MatchValue(value=value)
                            )
                        )
                    elif isinstance(value, (int, float)):
                        conditions.append(
                            FieldCondition(
                                key=key,
                                range=Range(gte=value, lte=value)
                            )
                        )
                
                if conditions:
                    search_filter = Filter(must=conditions)
            
            # For now, use text-based search (in production, you'd use embeddings)
            # This is a simplified implementation
            search_results = []
            
            # Get all documents and filter by text similarity
            all_points = self.client.scroll(
                collection_name=full_name,
                limit=1000
            )[0]
            
            for point in all_points:
                text = point.payload.get("text", "")
                score = self._calculate_text_similarity(query, text)
                
                if score > 0.1:  # Minimum similarity threshold
                    search_results.append(SearchResult(
                        document_id=point.id,
                        text=text,
                        metadata=point.payload,
                        score=score
                    ))
            
            # Sort by score and limit results
            search_results.sort(key=lambda x: x.score, reverse=True)
            return search_results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {e}")
            return []
    
    def _calculate_text_similarity(self, query: str, text: str) -> float:
        """Calculate text similarity between query and document text."""
        try:
            # Simple word overlap similarity
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            
            if not query_words or not text_words:
                return 0.0
            
            intersection = len(query_words.intersection(text_words))
            union = len(query_words.union(text_words))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    async def update_document(self, collection_name: str, document_id: str,
                            text: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Update an existing document in the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return False
            
            full_name = self._get_collection_name(collection_name)
            
            # Get existing document
            existing_doc = await self.get_document(collection_name, document_id)
            if not existing_doc:
                logger.warning(f"Document {document_id} not found for update")
                return False
            
            # Prepare updated metadata
            updated_metadata = existing_doc.metadata.copy()
            if text:
                updated_metadata["text"] = text
            if metadata:
                updated_metadata.update(metadata)
            
            updated_metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Update document
            return await self.add_document(
                collection_name=collection_name,
                document_id=document_id,
                text=text or existing_doc.text,
                metadata=updated_metadata,
                embedding=existing_doc.embedding
            )
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    async def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return False
            
            full_name = self._get_collection_name(collection_name)
            
            # Delete point
            self.client.delete(
                collection_name=full_name,
                points_selector=[document_id]
            )
            
            logger.info(f"Deleted document {document_id} from collection {full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def list_collections(self) -> List[str]:
        """List all collections in the vector database."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return []
            
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        try:
            if not self.client:
                logger.error("Qdrant client not initialized")
                return None
            
            full_name = self._get_collection_name(collection_name)
            
            info = self.client.get_collection(full_name)
            
            return {
                "name": info.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": str(info.config.params.vectors.distance)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            return None
    
    def close(self):
        """Close the vector database connection."""
        try:
            if self.client:
                self.client.close()
                logger.info("Vector database connection closed")
        except Exception as e:
            logger.error(f"Error closing vector database connection: {e}")


# Convenience functions for common operations
async def create_default_collections(vector_db: VectorDatabase) -> bool:
    """Create default collections for the job application system."""
    try:
        collections = [
            ("candidates", "Candidate profiles and preferences"),
            ("jobs", "Job postings and requirements"),
            ("matches", "Job-candidate matches"),
            ("conversations", "Agent conversation history")
        ]
        
        for collection_name, description in collections:
            success = await vector_db.create_collection(collection_name)
            if not success:
                logger.error(f"Failed to create collection: {collection_name}")
                return False
        
        logger.info("Created default collections")
        return True
        
    except Exception as e:
        logger.error(f"Error creating default collections: {e}")
        return False


async def initialize_vector_database(host: str = "localhost", port: int = 6333) -> VectorDatabase:
    """Initialize the vector database with default collections."""
    vector_db = VectorDatabase(host=host, port=port)
    
    if vector_db.client:
        await create_default_collections(vector_db)
    
    return vector_db 