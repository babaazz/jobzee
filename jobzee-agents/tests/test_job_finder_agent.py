#!/usr/bin/env python3
"""
Tests for Job Finder Agent

This module contains comprehensive tests for the Job Finder Agent,
including unit tests, integration tests, and workflow tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from job_finder_agent.agent import JobFinderAgent
from job_finder_agent.graph import create_job_finder_graph
from common.config import Config
from common.vector_db import VectorDatabase
from common.a2a_protocol import AgentToAgentProtocol
from common.kafka_client import KafkaClient


class TestJobFinderAgent:
    """Test cases for JobFinderAgent class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.openai.api_key = "test-key"
        config.openai.model = "gpt-4"
        config.kafka.bootstrap_servers = "localhost:9092"
        config.kafka.job_finder_topic = "job-finder-events"
        config.vector_db.index_path = "./test_index.faiss"
        config.vector_db.dimension = 1536
        return config

    @pytest.fixture
    def mock_vector_db(self):
        """Create a mock vector database."""
        vector_db = Mock(spec=VectorDatabase)
        vector_db.search.return_value = [
            {"id": "1", "score": 0.9, "content": "Software Engineer"},
            {"id": "2", "score": 0.8, "content": "Python Developer"},
        ]
        return vector_db

    @pytest.fixture
    def mock_a2a_protocol(self):
        """Create a mock A2A protocol."""
        protocol = Mock(spec=AgentToAgentProtocol)
        protocol.send_message = AsyncMock()
        protocol.send_heartbeat = AsyncMock()
        return protocol

    @pytest.fixture
    def agent(self, mock_config, mock_vector_db, mock_a2a_protocol):
        """Create a JobFinderAgent instance for testing."""
        return JobFinderAgent(
            config=mock_config,
            vector_db=mock_vector_db,
            a2a_protocol=mock_a2a_protocol
        )

    def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent is not None
        assert agent.config is not None
        assert agent.vector_db is not None
        assert agent.a2a_protocol is not None

    @pytest.mark.asyncio
    async def test_process_user_message(self, agent):
        """Test processing user messages."""
        message = "I'm looking for a Python developer job"
        user_id = "user123"
        session_id = "session456"

        # Mock the LLM response
        with patch.object(agent, '_get_llm_response') as mock_llm:
            mock_llm.return_value = "I found some Python developer positions for you."
            
            response = await agent.process_user_message(message, user_id, session_id)
            
            assert response is not None
            assert "Python developer" in response
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_jobs(self, agent):
        """Test job search functionality."""
        skills = ["Python", "Django", "PostgreSQL"]
        experience_level = "mid-level"
        location = "San Francisco"
        remote_ok = True

        jobs = await agent.search_jobs(
            skills=skills,
            experience_level=experience_level,
            location=location,
            remote_ok=remote_ok
        )

        assert isinstance(jobs, list)
        assert len(jobs) > 0
        agent.vector_db.search.assert_called()

    @pytest.mark.asyncio
    async def test_analyze_candidate_profile(self, agent):
        """Test candidate profile analysis."""
        profile_data = {
            "skills": ["Python", "JavaScript", "React"],
            "experience": "3 years",
            "education": "Bachelor's in Computer Science",
            "location": "New York"
        }

        analysis = await agent.analyze_candidate_profile(profile_data)
        
        assert analysis is not None
        assert "skills" in analysis
        assert "recommendations" in analysis

    @pytest.mark.asyncio
    async def test_generate_job_recommendations(self, agent):
        """Test job recommendation generation."""
        candidate_profile = {
            "skills": ["Python", "Django"],
            "experience": "2 years",
            "location": "Remote"
        }
        
        jobs = [
            {"id": "1", "title": "Python Developer", "company": "TechCorp"},
            {"id": "2", "title": "Backend Engineer", "company": "StartupXYZ"}
        ]

        recommendations = await agent.generate_job_recommendations(
            candidate_profile, jobs
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all("score" in rec for rec in recommendations)

    @pytest.mark.asyncio
    async def test_process_messages(self, agent):
        """Test message processing loop."""
        # Mock Kafka message
        mock_message = Mock()
        mock_message.value = b'{"type": "job_search", "data": {"skills": ["Python"]}}'
        
        with patch.object(agent.a2a_protocol, 'receive_message') as mock_receive:
            mock_receive.return_value = [mock_message]
            
            # Run for a short time
            await asyncio.wait_for(agent.process_messages(), timeout=0.1)
            
            mock_receive.assert_called()

    def test_extract_skills_from_text(self, agent):
        """Test skill extraction from text."""
        text = "I have experience with Python, JavaScript, and React. I also know Docker and AWS."
        
        skills = agent.extract_skills_from_text(text)
        
        assert isinstance(skills, list)
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills

    def test_calculate_match_score(self, agent):
        """Test match score calculation."""
        candidate_skills = ["Python", "Django", "PostgreSQL"]
        job_requirements = ["Python", "Django", "JavaScript", "AWS"]
        
        score = agent.calculate_match_score(candidate_skills, job_requirements)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_handle_job_event(self, agent):
        """Test handling job events."""
        job_event = {
            "type": "job_created",
            "data": {
                "id": "job123",
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "skills": ["Python", "Django", "AWS"]
            }
        }

        await agent.handle_job_event(job_event)
        
        # Verify that the job was processed
        assert agent.vector_db.add_document.called

    @pytest.mark.asyncio
    async def test_handle_candidate_event(self, agent):
        """Test handling candidate events."""
        candidate_event = {
            "type": "candidate_updated",
            "data": {
                "id": "candidate123",
                "skills": ["Python", "React"],
                "experience": "3 years"
            }
        }

        await agent.handle_candidate_event(candidate_event)
        
        # Verify that the candidate was processed
        assert agent.vector_db.add_document.called

    def test_validate_input_data(self, agent):
        """Test input data validation."""
        # Valid data
        valid_data = {
            "skills": ["Python", "Django"],
            "experience": "2 years",
            "location": "Remote"
        }
        assert agent.validate_input_data(valid_data) is True

        # Invalid data
        invalid_data = {
            "skills": "not a list",
            "experience": 123  # should be string
        }
        assert agent.validate_input_data(invalid_data) is False

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling in agent operations."""
        # Test with invalid input
        with pytest.raises(ValueError):
            await agent.process_user_message("", "", "")

        # Test with None input
        with pytest.raises(ValueError):
            await agent.search_jobs(skills=None, experience_level="", location="", remote_ok=False)


class TestJobFinderGraph:
    """Test cases for JobFinderGraph workflow."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for graph testing."""
        agent = Mock(spec=JobFinderAgent)
        agent.process_user_message = AsyncMock(return_value="Test response")
        agent.search_jobs = AsyncMock(return_value=[{"id": "1", "title": "Test Job"}])
        return agent

    def test_graph_creation(self, mock_agent):
        """Test that the graph is created successfully."""
        graph = create_job_finder_graph(mock_agent)
        assert graph is not None

    @pytest.mark.asyncio
    async def test_graph_execution(self, mock_agent):
        """Test graph execution with sample input."""
        graph = create_job_finder_graph(mock_agent)
        
        # Test input
        test_input = {
            "message": "I'm looking for a Python job",
            "user_id": "user123",
            "session_id": "session456"
        }
        
        # Execute graph
        result = await graph.ainvoke(test_input)
        
        assert result is not None
        assert "response" in result

    @pytest.mark.asyncio
    async def test_graph_with_job_search(self, mock_agent):
        """Test graph execution for job search."""
        graph = create_job_finder_graph(mock_agent)
        
        test_input = {
            "message": "Find me Python developer jobs in San Francisco",
            "user_id": "user123",
            "session_id": "session456",
            "intent": "job_search"
        }
        
        result = await graph.ainvoke(test_input)
        
        assert result is not None
        assert "jobs" in result or "response" in result


class TestIntegration:
    """Integration tests for the Job Finder Agent."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test the complete workflow from message to response."""
        # This would require a more complete setup with actual services
        # For now, we'll test the basic flow
        config = Config()
        vector_db = VectorDatabase(
            index_path="./test_index.faiss",
            dimension=1536
        )
        
        # Mock Kafka client
        kafka_client = Mock(spec=KafkaClient)
        a2a_protocol = AgentToAgentProtocol(
            kafka_client=kafka_client,
            agent_id="test_job_finder"
        )
        
        agent = JobFinderAgent(
            config=config,
            vector_db=vector_db,
            a2a_protocol=a2a_protocol
        )
        
        # Test basic functionality
        assert agent is not None
        
        # Cleanup
        vector_db.close()

    @pytest.mark.asyncio
    async def test_agent_communication(self):
        """Test communication between agents."""
        # Mock the A2A protocol
        kafka_client = Mock(spec=KafkaClient)
        a2a_protocol = AgentToAgentProtocol(
            kafka_client=kafka_client,
            agent_id="test_job_finder"
        )
        
        # Test sending a message
        message = {
            "type": "job_search_request",
            "data": {
                "skills": ["Python", "Django"],
                "experience": "2 years"
            }
        }
        
        await a2a_protocol.send_message(message)
        
        # Verify the message was sent
        assert kafka_client.send_message.called


if __name__ == "__main__":
    pytest.main([__file__]) 