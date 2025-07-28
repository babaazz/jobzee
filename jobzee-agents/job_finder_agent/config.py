import os
from typing import List

class JobFinderConfig:
    """Configuration for the Job Finder Agent"""
    
    def __init__(self):
        # Kafka Configuration
        self.kafka_brokers: List[str] = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
        self.job_requests_topic: str = os.getenv("JOB_REQUESTS_TOPIC", "job-requests")
        self.job_matches_topic: str = os.getenv("JOB_MATCHES_TOPIC", "job-matches")
        
        # Vector Database Configuration
        self.vector_db_url: str = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
        self.vector_db_collection: str = os.getenv("VECTOR_DB_COLLECTION", "jobs")
        
        # AI Model Configuration
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.model_name: str = os.getenv("MODEL_NAME", "gpt-4")
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
        
        # Matching Configuration
        self.min_match_score: float = float(os.getenv("MIN_MATCH_SCORE", "0.7"))
        self.max_results: int = int(os.getenv("MAX_RESULTS", "10"))
        
        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Agent Configuration
        self.agent_id: str = os.getenv("AGENT_ID", "job-finder-agent")
        self.agent_name: str = os.getenv("AGENT_NAME", "Job Finder Agent")
        self.agent_version: str = os.getenv("AGENT_VERSION", "1.0.0")
        
        # Health Check Configuration
        self.health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        self.max_processing_time: int = int(os.getenv("MAX_PROCESSING_TIME", "300")) 