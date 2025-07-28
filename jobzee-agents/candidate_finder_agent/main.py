#!/usr/bin/env python3
"""
Candidate Finder Agent - Main Entry Point

This agent is responsible for finding and matching candidates with jobs
based on job requirements and candidate profiles.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.a2a_protocol import AgentToAgentProtocol
from common.config import Config
from common.kafka_client import KafkaClient
from common.vector_db import VectorDatabase
from candidate_finder_agent.agent import CandidateFinderAgent
from candidate_finder_agent.graph import create_candidate_finder_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the Candidate Finder Agent."""
    try:
        # Load configuration
        config = Config()
        logger.info("Configuration loaded successfully")

        # Initialize Kafka client
        kafka_client = KafkaClient(
            bootstrap_servers=config.kafka.bootstrap_servers,
            topic=config.kafka.candidate_finder_topic
        )
        logger.info("Kafka client initialized")

        # Initialize vector database
        vector_db = VectorDatabase(
            index_path=config.vector_db.index_path,
            dimension=config.vector_db.dimension
        )
        logger.info("Vector database initialized")

        # Initialize agent-to-agent protocol
        a2a_protocol = AgentToAgentProtocol(
            kafka_client=kafka_client,
            agent_id="candidate_finder_agent"
        )
        logger.info("Agent-to-agent protocol initialized")

        # Create the candidate finder agent
        agent = CandidateFinderAgent(
            config=config,
            vector_db=vector_db,
            a2a_protocol=a2a_protocol
        )
        logger.info("Candidate Finder Agent created")

        # Create the LangGraph workflow
        graph = create_candidate_finder_graph(agent)
        logger.info("Candidate Finder Graph created")

        # Start the agent
        logger.info("Starting Candidate Finder Agent...")
        
        # Run the agent in a loop
        while True:
            try:
                # Process incoming messages
                await agent.process_messages()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    except Exception as e:
        logger.error(f"Failed to start Candidate Finder Agent: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'kafka_client' in locals():
            await kafka_client.close()
        if 'vector_db' in locals():
            vector_db.close()
        logger.info("Candidate Finder Agent shutdown complete")


if __name__ == "__main__":
    asyncio.run(main()) 