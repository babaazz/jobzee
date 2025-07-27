# Multi-Agent Agents

Python-based AI agents for the Multi-Agent Job Application System using LangChain, LangGraph, and FAISS for intelligent job-candidate matching.

## Tech Stack

- **Language**: Python 3.11+
- **AI Framework**: LangChain, LangGraph
- **LLM**: OpenAI GPT models
- **Vector Database**: FAISS
- **Message Queue**: Apache Kafka
- **Vector Search**: ChromaDB
- **Data Processing**: Pandas, NumPy
- **Configuration**: Pydantic Settings

## Architecture

The system consists of two main AI agents:

1. **Job Finder Agent** (`job_finder_agent/`) - Finds and matches jobs with candidates
2. **Candidate Finder Agent** (`candidate_finder_agent/`) - Finds and matches candidates with jobs

### Agent Communication

Agents communicate using a standardized protocol (`common/a2a_protocol.py`) over Kafka:

- **Message Types**: Job events, candidate events, match requests/responses
- **Data Structures**: JobData, CandidateData, MatchRequest, MatchResponse
- **Coordination**: Heartbeats, status updates, error handling

## Prerequisites

- Python 3.11+
- Apache Kafka 2.8+
- Redis 6+ (optional, for caching)
- OpenAI API key

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd multi-agent-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_JOB_FINDER_TOPIC=job-finder-events
KAFKA_CANDIDATE_FINDER_TOPIC=candidate-finder-events

# Vector Database Configuration
VECTOR_DB_INDEX_PATH=./data/vector_db/jobzee_index.faiss
VECTOR_DB_DIMENSION=1536

# Agent Configuration
AGENT_LOG_LEVEL=INFO
AGENT_HEARTBEAT_INTERVAL=30

# Database Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Running Agents

### Job Finder Agent

```bash
# Start the job finder agent
python job_finder_agent/main.py
```

The Job Finder Agent will:

- Listen for job creation/update events
- Process candidate profiles
- Find matching jobs for candidates
- Send match responses

### Candidate Finder Agent

```bash
# Start the candidate finder agent
python candidate_finder_agent/main.py
```

The Candidate Finder Agent will:

- Listen for candidate creation/update events
- Process job requirements
- Find matching candidates for jobs
- Send match responses

### Running Both Agents

```bash
# Terminal 1: Job Finder Agent
python job_finder_agent/main.py

# Terminal 2: Candidate Finder Agent
python candidate_finder_agent/main.py
```

## Docker

```bash
# Build the image
docker build -t multi-agent-agents .

# Run Job Finder Agent
docker run -d \
  --name job-finder-agent \
  --env-file .env \
  multi-agent-agents \
  python job_finder_agent/main.py

# Run Candidate Finder Agent
docker run -d \
  --name candidate-finder-agent \
  --env-file .env \
  multi-agent-agents \
  python candidate_finder_agent/main.py
```

## Project Structure

```
├── job_finder_agent/          # Job Finder Agent
│   ├── main.py               # Entry point
│   ├── agent.py              # Agent implementation
│   ├── graph.py              # LangGraph workflow
│   └── prompts.py            # LLM prompts
├── candidate_finder_agent/    # Candidate Finder Agent
│   ├── main.py               # Entry point
│   ├── agent.py              # Agent implementation
│   ├── graph.py              # LangGraph workflow
│   └── prompts.py            # LLM prompts
├── common/                   # Shared components
│   ├── a2a_protocol.py      # Agent communication protocol
│   ├── config.py            # Configuration management
│   ├── kafka_client.py      # Kafka client wrapper
│   ├── vector_db.py         # FAISS vector database interface
│   └── langgraph_utils.py   # LangGraph utilities
├── data/                    # Data storage
│   ├── vector_db/           # FAISS index files
│   └── logs/                # Log files
└── tests/                   # Test files
```

## Agent Workflows

### Job Finder Agent Workflow

1. **Receive Job Event** - Listen for job creation/updates
2. **Process Job Data** - Extract requirements and skills
3. **Vectorize Job** - Create embedding for similarity search
4. **Search Candidates** - Find matching candidates in vector DB
5. **Rank Matches** - Use LLM to rank and score matches
6. **Send Response** - Send match results to requesting agent

### Candidate Finder Agent Workflow

1. **Receive Candidate Event** - Listen for candidate creation/updates
2. **Process Candidate Data** - Extract skills and experience
3. **Vectorize Candidate** - Create embedding for similarity search
4. **Search Jobs** - Find matching jobs in vector DB
5. **Rank Matches** - Use LLM to rank and score matches
6. **Send Response** - Send match results to requesting agent

## Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_job_finder_agent.py
```

### Adding New Agents

1. Create agent directory: `mkdir new_agent`
2. Implement agent logic in `new_agent/agent.py`
3. Create LangGraph workflow in `new_agent/graph.py`
4. Add entry point in `new_agent/main.py`
5. Register message handlers in the agent

## Monitoring

### Health Checks

Agents send heartbeat messages every 30 seconds:

```python
await a2a_protocol.send_heartbeat()
```

### Logging

Structured logging with different levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General information about agent operations
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations

### Metrics

Track agent performance:

- Messages processed per second
- Match accuracy scores
- Response times
- Error rates

## Troubleshooting

### Common Issues

1. **Kafka Connection Failed**

   - Check Kafka server is running
   - Verify bootstrap servers configuration
   - Check network connectivity

2. **OpenAI API Errors**

   - Verify API key is correct
   - Check API quota and limits
   - Ensure model name is valid

3. **Vector Database Issues**
   - Check disk space for index files
   - Verify FAISS installation
   - Check index file permissions

### Debug Mode

Enable debug logging:

```bash
export AGENT_LOG_LEVEL=DEBUG
python job_finder_agent/main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
