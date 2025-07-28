#!/usr/bin/env python3
"""
Job Finder Agent HTTP Server

FastAPI server for the Job Finder Agent with WebSocket support,
authentication, and real-time communication.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.config import Config
from common.kafka_client import KafkaClient
from common.vector_db import VectorDatabase
from common.a2a_protocol import AgentToAgentProtocol
from job_finder_agent.agent import JobFinderAgent
from job_finder_agent.graph import create_job_finder_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('job_finder_requests_total', 'Total requests to Job Finder Agent')
REQUEST_DURATION = Histogram('job_finder_request_duration_seconds', 'Request duration in seconds')
WEBSOCKET_CONNECTIONS = Counter('job_finder_websocket_connections_total', 'Total WebSocket connections')

# Security
security = HTTPBearer()

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    timestamp: str = Field(..., description="Response timestamp")

class JobSearchRequest(BaseModel):
    skills: List[str] = Field(..., description="Required skills")
    experience_level: str = Field(..., description="Experience level")
    location: Optional[str] = Field(None, description="Preferred location")
    remote_ok: bool = Field(False, description="Remote work acceptable")

class JobSearchResponse(BaseModel):
    jobs: List[Dict] = Field(..., description="Matching jobs")
    total_count: int = Field(..., description="Total matching jobs")
    search_id: str = Field(..., description="Search session ID")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    agent_id: str = Field(..., description="Agent ID")
    uptime: float = Field(..., description="Uptime in seconds")

class JobFinderHTTPServer:
    def __init__(self):
        self.app = FastAPI(
            title="Job Finder Agent API",
            description="HTTP API for the Job Finder Agent",
            version="1.0.0"
        )
        
        # Initialize components
        self.config = Config()
        self.kafka_client = None
        self.vector_db = None
        self.a2a_protocol = None
        self.agent = None
        self.graph = None
        
        # WebSocket connection manager
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Setup routes and middleware
        self.setup_middleware()
        self.setup_routes()
        
        # Startup/shutdown events
        self.app.add_event_handler("startup", self.startup_event)
        self.app.add_event_handler("shutdown", self.shutdown_event)
    
    def setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            REQUEST_COUNT.inc()
            return HealthResponse(
                status="healthy",
                agent_id="job_finder_agent",
                uptime=0.0  # TODO: Implement uptime tracking
            )
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            return generate_latest()
        
        @self.app.post("/chat", response_model=ChatResponse)
        async def chat_with_agent(
            message: ChatMessage,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Chat with the Job Finder Agent."""
            REQUEST_COUNT.inc()
            
            # TODO: Implement proper authentication
            if not self.verify_token(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            try:
                # Process message through agent
                response = await self.agent.process_user_message(
                    message.message,
                    user_id=message.user_id,
                    session_id=message.session_id
                )
                
                return ChatResponse(
                    response=response,
                    session_id=message.session_id or "default",
                    timestamp=str(asyncio.get_event_loop().time())
                )
                
            except Exception as e:
                logger.error(f"Error processing chat message: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process message"
                )
        
        @self.app.post("/search/jobs", response_model=JobSearchResponse)
        async def search_jobs(
            request: JobSearchRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Search for jobs based on criteria."""
            REQUEST_COUNT.inc()
            
            # TODO: Implement proper authentication
            if not self.verify_token(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            try:
                # Search jobs using agent
                jobs = await self.agent.search_jobs(
                    skills=request.skills,
                    experience_level=request.experience_level,
                    location=request.location,
                    remote_ok=request.remote_ok
                )
                
                return JobSearchResponse(
                    jobs=jobs,
                    total_count=len(jobs),
                    search_id=f"search_{asyncio.get_event_loop().time()}"
                )
                
            except Exception as e:
                logger.error(f"Error searching jobs: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to search jobs"
                )
        
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time communication."""
            await websocket.accept()
            WEBSOCKET_CONNECTIONS.inc()
            
            # Store connection
            self.active_connections[user_id] = websocket
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Process message
                    response = await self.agent.process_user_message(
                        message_data.get("message", ""),
                        user_id=user_id,
                        session_id=message_data.get("session_id")
                    )
                    
                    # Send response
                    await websocket.send_text(json.dumps({
                        "response": response,
                        "session_id": message_data.get("session_id"),
                        "timestamp": str(asyncio.get_event_loop().time())
                    }))
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {e}")
            finally:
                # Remove connection
                if user_id in self.active_connections:
                    del self.active_connections[user_id]
    
    def verify_token(self, token: str) -> bool:
        """Verify authentication token."""
        # TODO: Implement proper JWT token verification
        # For now, accept any non-empty token
        return bool(token and token.strip())
    
    async def startup_event(self):
        """Initialize components on startup."""
        try:
            logger.info("Starting Job Finder Agent HTTP Server...")
            
            # Initialize Kafka client
            self.kafka_client = KafkaClient(
                bootstrap_servers=self.config.kafka.bootstrap_servers,
                topic=self.config.kafka.job_finder_topic
            )
            logger.info("Kafka client initialized")
            
            # Initialize vector database
            self.vector_db = VectorDatabase(
                index_path=self.config.vector_db.index_path,
                dimension=self.config.vector_db.dimension
            )
            logger.info("Vector database initialized")
            
            # Initialize agent-to-agent protocol
            self.a2a_protocol = AgentToAgentProtocol(
                kafka_client=self.kafka_client,
                agent_id="job_finder_agent"
            )
            logger.info("Agent-to-agent protocol initialized")
            
            # Create the job finder agent
            self.agent = JobFinderAgent(
                config=self.config,
                vector_db=self.vector_db,
                a2a_protocol=self.a2a_protocol
            )
            logger.info("Job Finder Agent created")
            
            # Create the LangGraph workflow
            self.graph = create_job_finder_graph(self.agent)
            logger.info("Job Finder Graph created")
            
            logger.info("Job Finder Agent HTTP Server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Job Finder Agent HTTP Server: {e}")
            raise
    
    async def shutdown_event(self):
        """Cleanup on shutdown."""
        try:
            logger.info("Shutting down Job Finder Agent HTTP Server...")
            
            # Close WebSocket connections
            for user_id, websocket in self.active_connections.items():
                await websocket.close()
            
            # Cleanup components
            if self.kafka_client:
                await self.kafka_client.close()
            if self.vector_db:
                self.vector_db.close()
            
            logger.info("Job Finder Agent HTTP Server shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point for the HTTP server."""
    server = JobFinderHTTPServer()
    
    # Get port from environment or use default
    port = int(os.getenv("AGENT_HTTP_PORT", 8084))
    host = os.getenv("AGENT_HTTP_HOST", "0.0.0.0")
    
    # Run the server
    uvicorn.run(
        server.app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 