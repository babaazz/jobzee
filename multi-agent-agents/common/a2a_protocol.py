"""
Agent-to-Agent Communication Protocol

This module defines the communication protocol between different agents
in the multi-agent job application system.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be exchanged between agents."""
    
    # Job-related messages
    JOB_CREATED = "job_created"
    JOB_UPDATED = "job_updated"
    JOB_DELETED = "job_deleted"
    
    # Candidate-related messages
    CANDIDATE_CREATED = "candidate_created"
    CANDIDATE_UPDATED = "candidate_updated"
    CANDIDATE_DELETED = "candidate_deleted"
    
    # Application-related messages
    APPLICATION_CREATED = "application_created"
    APPLICATION_UPDATED = "application_updated"
    APPLICATION_DELETED = "application_deleted"
    
    # Matching messages
    MATCH_REQUEST = "match_request"
    MATCH_RESPONSE = "match_response"
    MATCH_FOUND = "match_found"
    
    # Agent coordination messages
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_STATUS = "agent_status"
    AGENT_ERROR = "agent_error"


@dataclass
class Message:
    """Base message structure for agent communication."""
    
    message_id: str
    message_type: MessageType
    sender_id: str
    receiver_id: Optional[str] = None
    timestamp: datetime = None
    payload: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.payload is None:
            self.payload = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class JobData:
    """Job data structure."""
    
    job_id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    skills: List[str]
    experience_level: str
    salary_range: Optional[str] = None
    job_type: str = "full-time"
    remote_friendly: bool = False


@dataclass
class CandidateData:
    """Candidate data structure."""
    
    candidate_id: str
    name: str
    email: str
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    location: str
    experience_years: int
    preferred_roles: List[str] = None
    salary_expectation: Optional[str] = None


@dataclass
class MatchRequest:
    """Match request structure."""
    
    request_id: str
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    criteria: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, urgent


@dataclass
class MatchResponse:
    """Match response structure."""
    
    request_id: str
    matches: List[Dict[str, Any]]
    confidence_scores: List[float]
    reasoning: str = ""


class AgentToAgentProtocol:
    """Protocol for agent-to-agent communication."""
    
    def __init__(self, kafka_client, agent_id: str):
        self.kafka_client = kafka_client
        self.agent_id = agent_id
        self.message_handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler(MessageType.AGENT_HEARTBEAT, self._handle_heartbeat)
        self.register_handler(MessageType.AGENT_STATUS, self._handle_status)
        self.register_handler(MessageType.AGENT_ERROR, self._handle_error)
    
    def register_handler(self, message_type: MessageType, handler):
        """Register a message handler for a specific message type."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type.value}")
    
    async def send_message(self, message: Message) -> bool:
        """Send a message to another agent."""
        try:
            message_data = message.to_dict()
            await self.kafka_client.publish_message(message_data)
            logger.info(f"Sent message {message.message_id} to {message.receiver_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def broadcast_message(self, message_type: MessageType, payload: Dict[str, Any]) -> bool:
        """Broadcast a message to all agents."""
        message = Message(
            message_id=f"{self.agent_id}_{datetime.utcnow().timestamp()}",
            message_type=message_type,
            sender_id=self.agent_id,
            payload=payload
        )
        return await self.send_message(message)
    
    async def send_match_request(self, receiver_id: str, match_request: MatchRequest) -> bool:
        """Send a match request to another agent."""
        message = Message(
            message_id=match_request.request_id,
            message_type=MessageType.MATCH_REQUEST,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            payload=match_request.__dict__
        )
        return await self.send_message(message)
    
    async def send_match_response(self, receiver_id: str, match_response: MatchResponse) -> bool:
        """Send a match response to another agent."""
        message = Message(
            message_id=f"response_{match_response.request_id}",
            message_type=MessageType.MATCH_RESPONSE,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            payload=match_response.__dict__
        )
        return await self.send_message(message)
    
    async def process_message(self, message_data: Dict[str, Any]) -> bool:
        """Process an incoming message."""
        try:
            message = Message.from_dict(message_data)
            
            # Check if message is for this agent
            if message.receiver_id and message.receiver_id != self.agent_id:
                logger.debug(f"Message {message.message_id} not for this agent")
                return False
            
            # Handle message based on type
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(message)
                logger.info(f"Processed message {message.message_id}")
                return True
            else:
                logger.warning(f"No handler for message type: {message.message_type.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def _handle_heartbeat(self, message: Message):
        """Handle heartbeat messages."""
        logger.debug(f"Received heartbeat from {message.sender_id}")
    
    async def _handle_status(self, message: Message):
        """Handle status messages."""
        logger.info(f"Agent {message.sender_id} status: {message.payload}")
    
    async def _handle_error(self, message: Message):
        """Handle error messages."""
        logger.error(f"Agent {message.sender_id} error: {message.payload}")
    
    async def send_heartbeat(self):
        """Send a heartbeat message."""
        await self.broadcast_message(
            MessageType.AGENT_HEARTBEAT,
            {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def send_status(self, status: str, details: Dict[str, Any] = None):
        """Send a status message."""
        payload = {"status": status, "details": details or {}}
        await self.broadcast_message(MessageType.AGENT_STATUS, payload)
    
    async def send_error(self, error: str, details: Dict[str, Any] = None):
        """Send an error message."""
        payload = {"error": error, "details": details or {}}
        await self.broadcast_message(MessageType.AGENT_ERROR, payload) 