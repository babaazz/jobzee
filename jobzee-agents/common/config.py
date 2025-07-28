import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Common configuration for all agents"""
    
    # Agent identification
    agent_id: str
    agent_name: str
    agent_version: str
    
    # Kafka configuration
    kafka_brokers: List[str]
    kafka_group_id: str
    
    # Vector database configuration
    vector_db_url: str
    vector_db_collection: str
    
    # AI model configuration
    openai_api_key: str
    model_name: str
    max_tokens: int
    temperature: float
    
    # Logging configuration
    log_level: str
    log_format: str
    
    # Health check configuration
    health_check_interval: int
    max_processing_time: int
    
    @classmethod
    def from_env(cls, agent_id: str, agent_name: str, agent_version: str = "1.0.0") -> 'AgentConfig':
        """Create configuration from environment variables"""
        return cls(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_version=agent_version,
            kafka_brokers=os.getenv("KAFKA_BROKERS", "localhost:9092").split(","),
            kafka_group_id=os.getenv("KAFKA_GROUP_ID", f"{agent_id}-group"),
            vector_db_url=os.getenv("VECTOR_DB_URL", "http://localhost:6333"),
            vector_db_collection=os.getenv("VECTOR_DB_COLLECTION", "default"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            model_name=os.getenv("MODEL_NAME", "gpt-4"),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
            max_processing_time=int(os.getenv("MAX_PROCESSING_TIME", "300"))
        )

@dataclass
class JobFinderConfig(AgentConfig):
    """Configuration specific to Job Finder Agent"""
    
    # Job finder specific topics
    job_requests_topic: str
    job_matches_topic: str
    
    # Matching configuration
    min_match_score: float
    max_results: int
    
    @classmethod
    def from_env(cls) -> 'JobFinderConfig':
        """Create Job Finder configuration from environment variables"""
        base_config = AgentConfig.from_env(
            agent_id=os.getenv("AGENT_ID", "job-finder-agent"),
            agent_name=os.getenv("AGENT_NAME", "Job Finder Agent"),
            agent_version=os.getenv("AGENT_VERSION", "1.0.0")
        )
        
        return cls(
            **base_config.__dict__,
            job_requests_topic=os.getenv("JOB_REQUESTS_TOPIC", "job-requests"),
            job_matches_topic=os.getenv("JOB_MATCHES_TOPIC", "job-matches"),
            min_match_score=float(os.getenv("MIN_MATCH_SCORE", "0.7")),
            max_results=int(os.getenv("MAX_RESULTS", "10"))
        )

@dataclass
class CandidateFinderConfig(AgentConfig):
    """Configuration specific to Candidate Finder Agent"""
    
    # Candidate finder specific topics
    candidate_requests_topic: str
    candidate_matches_topic: str
    
    # Screening configuration
    min_candidate_score: float
    max_candidates: int
    
    @classmethod
    def from_env(cls) -> 'CandidateFinderConfig':
        """Create Candidate Finder configuration from environment variables"""
        base_config = AgentConfig.from_env(
            agent_id=os.getenv("AGENT_ID", "candidate-finder-agent"),
            agent_name=os.getenv("AGENT_NAME", "Candidate Finder Agent"),
            agent_version=os.getenv("AGENT_VERSION", "1.0.0")
        )
        
        return cls(
            **base_config.__dict__,
            candidate_requests_topic=os.getenv("CANDIDATE_REQUESTS_TOPIC", "candidate-requests"),
            candidate_matches_topic=os.getenv("CANDIDATE_MATCHES_TOPIC", "candidate-matches"),
            min_candidate_score=float(os.getenv("MIN_CANDIDATE_SCORE", "0.7")),
            max_candidates=int(os.getenv("MAX_CANDIDATES", "10"))
        )

class ConfigManager:
    """Manager for handling configuration across agents"""
    
    def __init__(self):
        self.configs: Dict[str, AgentConfig] = {}
        
    def register_config(self, name: str, config: AgentConfig):
        """Register a configuration"""
        self.configs[name] = config
        
    def get_config(self, name: str) -> AgentConfig:
        """Get a configuration by name"""
        if name not in self.configs:
            raise ValueError(f"Configuration '{name}' not found")
        return self.configs[name]
        
    def validate_config(self, config: AgentConfig) -> bool:
        """Validate a configuration"""
        required_fields = [
            'agent_id', 'agent_name', 'kafka_brokers', 
            'openai_api_key', 'vector_db_url'
        ]
        
        for field in required_fields:
            if not getattr(config, field, None):
                return False
                
        return True
        
    def get_all_configs(self) -> Dict[str, AgentConfig]:
        """Get all registered configurations"""
        return self.configs.copy()
        
    def export_configs(self) -> Dict[str, Dict[str, Any]]:
        """Export configurations as dictionaries"""
        return {
            name: config.__dict__ 
            for name, config in self.configs.items()
        } 