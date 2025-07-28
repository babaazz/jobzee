# JobZee Agents Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agent Types](#agent-types)
4. [LangGraph Workflows](#langgraph-workflows)
5. [Vector Database Integration](#vector-database-integration)
6. [Communication Protocols](#communication-protocols)
7. [MCP Tools Integration](#mcp-tools-integration)
8. [API Design](#api-design)
9. [Testing Strategy](#testing-strategy)
10. [Deployment](#deployment)

## Overview

The JobZee Agents repository contains AI-powered agents built with Python, LangChain, and LangGraph. These agents handle intelligent job matching, candidate analysis, and automated recruitment workflows.

### Key Features

- **Intelligent Matching**: AI-powered job-candidate matching using vector similarity
- **Natural Language Processing**: Advanced NLP for understanding job requirements and candidate profiles
- **Workflow Automation**: LangGraph-powered state machines for complex workflows
- **Real-time Communication**: WebSocket and HTTP APIs for real-time interactions
- **Tool Integration**: MCP (Model Context Protocol) for external tool access
- **Vector Search**: Semantic search using Qdrant vector database

## Architecture

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │ Job Finder      │    │ Candidate       │    │ Common        │ │
│  │ Agent           │    │ Finder Agent    │    │ Components    │ │
│  │                 │    │                 │    │               │ │
│  │ • Job Matching  │    │ • Candidate     │    │ • A2A Protocol│ │
│  │ • Profile       │    │   Analysis      │    │ • Vector DB   │ │
│  │   Analysis      │    │ • Portfolio     │    │ • Kafka       │ │
│  │ • Interview     │    │   Analysis      │    │ • MCP Client  │ │
│  │   Coordination  │    │ • Recruitment   │    │ • Config      │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │ LangGraph       │    │ Vector Database │    │ External      │ │
│  │ Workflows       │    │ (Qdrant)        │    │ Tools         │ │
│  │                 │    │                 │    │               │ │
│  │ • State         │    │ • Embeddings    │    │ • GitHub API  │ │
│  │   Machines      │    │ • Similarity    │    │ • Email       │ │
│  │ • Orchestration │    │   Search        │    │ • Calendar    │ │
│  │ • Memory        │    │ • Collections   │    │ • LinkedIn    │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
jobzee-agents/
├── job_finder_agent/          # Job finder agent
│   ├── main.py               # Agent entry point
│   ├── http_server.py        # HTTP API server
│   ├── config.py             # Agent configuration
│   ├── embeddings.py         # Embedding generation
│   ├── kafka_consumer.py     # Kafka event consumer
│   └── workflows/            # LangGraph workflows
│       ├── __init__.py
│       ├── match_jobs.py     # Job matching workflow
│       ├── apply_jobs.py     # Job application workflow
│       └── collect_preferences.py # Preference collection
├── candidate_finder_agent/   # Candidate finder agent
│   ├── main.py               # Agent entry point
│   ├── http_server.py        # HTTP API server
│   ├── config.py             # Agent configuration
│   └── workflows/            # LangGraph workflows
│       └── analyze_candidates.py # Candidate analysis
├── common/                   # Shared components
│   ├── a2a_protocol.py      # Agent-to-agent protocol
│   ├── config.py            # Common configuration
│   ├── langgraph_utils.py   # LangGraph utilities
│   ├── mcp_client.py        # MCP client
│   └── vector_db.py         # Vector database client
├── tests/                   # Test suite
│   └── test_job_finder_agent.py
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container configuration
```

## Agent Types

### Job Finder Agent

**Purpose**: Assists candidates in finding suitable job opportunities and managing their job search process.

**Key Responsibilities**:

- Analyze candidate profiles and preferences
- Search for matching job opportunities
- Provide personalized job recommendations
- Assist with job applications
- Coordinate interview scheduling
- Track application status

**Core Workflows**:

1. **Profile Analysis**: Analyze candidate skills, experience, and preferences
2. **Job Matching**: Find jobs that match candidate profile
3. **Application Assistance**: Help with job applications
4. **Interview Coordination**: Schedule and prepare for interviews

```python
# job_finder_agent/main.py
class JobFinderAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.vector_db = QdrantClient(url=config.vector_db_url)
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_profile", self.analyze_profile)
        workflow.add_node("search_jobs", self.search_jobs)
        workflow.add_node("rank_jobs", self.rank_jobs)
        workflow.add_node("generate_recommendations", self.generate_recommendations)

        # Add edges
        workflow.set_entry_point("analyze_profile")
        workflow.add_edge("analyze_profile", "search_jobs")
        workflow.add_edge("search_jobs", "rank_jobs")
        workflow.add_edge("rank_jobs", "generate_recommendations")

        return workflow.compile()

    async def process_request(self, request: JobRequest) -> JobResponse:
        """Process a job search request"""
        state = AgentState(
            candidate_id=request.candidate_id,
            preferences=request.preferences,
            message=request.message
        )

        result = await self.workflow.ainvoke(state)
        return JobResponse(
            recommendations=result.recommendations,
            reasoning=result.reasoning,
            next_steps=result.next_steps
        )
```

### Candidate Finder Agent

**Purpose**: Assists HR professionals in finding suitable candidates for job openings.

**Key Responsibilities**:

- Analyze job requirements and company needs
- Search for matching candidates
- Evaluate candidate profiles and portfolios
- Provide candidate recommendations
- Assist with recruitment workflow
- Coordinate candidate outreach

**Core Workflows**:

1. **Job Analysis**: Understand job requirements and company culture
2. **Candidate Search**: Find candidates matching job criteria
3. **Profile Evaluation**: Analyze candidate skills and experience
4. **Recommendation Generation**: Provide ranked candidate list

```python
# candidate_finder_agent/main.py
class CandidateFinderAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.vector_db = QdrantClient(url=config.vector_db_url)
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_job", self.analyze_job)
        workflow.add_node("search_candidates", self.search_candidates)
        workflow.add_node("evaluate_candidates", self.evaluate_candidates)
        workflow.add_node("generate_recommendations", self.generate_recommendations)

        # Add edges
        workflow.set_entry_point("analyze_job")
        workflow.add_edge("analyze_job", "search_candidates")
        workflow.add_edge("search_candidates", "evaluate_candidates")
        workflow.add_edge("evaluate_candidates", "generate_recommendations")

        return workflow.compile()

    async def process_request(self, request: CandidateRequest) -> CandidateResponse:
        """Process a candidate search request"""
        state = AgentState(
            job_id=request.job_id,
            requirements=request.requirements,
            message=request.message
        )

        result = await self.workflow.ainvoke(state)
        return CandidateResponse(
            candidates=result.candidates,
            reasoning=result.reasoning,
            next_steps=result.next_steps
        )
```

## LangGraph Workflows

### Job Matching Workflow

```python
# job_finder_agent/workflows/match_jobs.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import asyncio

class JobMatchingState(TypedDict):
    candidate_id: str
    preferences: dict
    message: str
    profile_analysis: dict
    job_matches: List[dict]
    ranked_jobs: List[dict]
    recommendations: List[dict]
    reasoning: str
    next_steps: List[str]

def create_job_matching_workflow() -> StateGraph:
    workflow = StateGraph(JobMatchingState)

    # Add nodes
    workflow.add_node("analyze_profile", analyze_candidate_profile)
    workflow.add_node("search_jobs", search_matching_jobs)
    workflow.add_node("rank_jobs", rank_job_matches)
    workflow.add_node("generate_recommendations", generate_job_recommendations)

    # Define edges
    workflow.set_entry_point("analyze_profile")
    workflow.add_edge("analyze_profile", "search_jobs")
    workflow.add_edge("search_jobs", "rank_jobs")
    workflow.add_edge("rank_jobs", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()

async def analyze_candidate_profile(state: JobMatchingState) -> JobMatchingState:
    """Analyze candidate profile and extract preferences"""
    candidate_id = state["candidate_id"]

    # Get candidate data from backend
    candidate_data = await get_candidate_profile(candidate_id)

    # Analyze skills, experience, and preferences
    analysis_prompt = f"""
    Analyze the following candidate profile and extract key information:

    Skills: {candidate_data['skills']}
    Experience: {candidate_data['experience']}
    Education: {candidate_data['education']}
    Portfolio: {candidate_data['portfolio_links']}

    Extract:
    1. Technical skills and proficiency levels
    2. Industry experience and domain knowledge
    3. Career goals and preferences
    4. Preferred job characteristics
    """

    response = await llm.ainvoke(analysis_prompt)

    return {
        **state,
        "profile_analysis": parse_analysis_response(response)
    }

async def search_matching_jobs(state: JobMatchingState) -> JobMatchingState:
    """Search for jobs matching candidate profile"""
    profile_analysis = state["profile_analysis"]

    # Generate search query from profile analysis
    search_query = generate_search_query(profile_analysis)

    # Search vector database
    job_matches = await vector_db.search(
        collection_name="jobs",
        query_vector=generate_embedding(search_query),
        limit=50
    )

    # Filter and enrich job data
    enriched_jobs = await enrich_job_data(job_matches)

    return {
        **state,
        "job_matches": enriched_jobs
    }

async def rank_job_matches(state: JobMatchingState) -> JobMatchingState:
    """Rank job matches based on candidate preferences"""
    profile_analysis = state["profile_analysis"]
    job_matches = state["job_matches"]

    # Calculate match scores
    ranked_jobs = []
    for job in job_matches:
        score = calculate_match_score(profile_analysis, job)
        ranked_jobs.append({
            **job,
            "match_score": score
        })

    # Sort by match score
    ranked_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        **state,
        "ranked_jobs": ranked_jobs[:10]  # Top 10 matches
    }

async def generate_job_recommendations(state: JobMatchingState) -> JobMatchingState:
    """Generate personalized job recommendations"""
    ranked_jobs = state["ranked_jobs"]
    profile_analysis = state["profile_analysis"]

    # Generate recommendations with reasoning
    recommendations_prompt = f"""
    Based on the candidate profile and top job matches, generate personalized recommendations:

    Candidate Profile: {profile_analysis}
    Top Job Matches: {ranked_jobs[:5]}

    Provide:
    1. Top 3 job recommendations with reasoning
    2. Key factors that make each job a good match
    3. Suggested next steps for the candidate
    """

    response = await llm.ainvoke(recommendations_prompt)

    return {
        **state,
        "recommendations": parse_recommendations(response),
        "reasoning": extract_reasoning(response),
        "next_steps": extract_next_steps(response)
    }
```

### Candidate Analysis Workflow

```python
# candidate_finder_agent/workflows/analyze_candidates.py
class CandidateAnalysisState(TypedDict):
    job_id: str
    requirements: dict
    message: str
    job_analysis: dict
    candidate_matches: List[dict]
    evaluated_candidates: List[dict]
    recommendations: List[dict]
    reasoning: str
    next_steps: List[str]

def create_candidate_analysis_workflow() -> StateGraph:
    workflow = StateGraph(CandidateAnalysisState)

    # Add nodes
    workflow.add_node("analyze_job", analyze_job_requirements)
    workflow.add_node("search_candidates", search_matching_candidates)
    workflow.add_node("evaluate_candidates", evaluate_candidate_profiles)
    workflow.add_node("generate_recommendations", generate_candidate_recommendations)

    # Define edges
    workflow.set_entry_point("analyze_job")
    workflow.add_edge("analyze_job", "search_candidates")
    workflow.add_edge("search_candidates", "evaluate_candidates")
    workflow.add_edge("evaluate_candidates", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()

async def analyze_job_requirements(state: CandidateAnalysisState) -> CandidateAnalysisState:
    """Analyze job requirements and extract key criteria"""
    job_id = state["job_id"]

    # Get job data from backend
    job_data = await get_job_details(job_id)

    # Analyze job requirements
    analysis_prompt = f"""
    Analyze the following job posting and extract key requirements:

    Title: {job_data['title']}
    Company: {job_data['company']}
    Description: {job_data['description']}
    Requirements: {job_data['requirements']}

    Extract:
    1. Required technical skills and proficiency levels
    2. Experience requirements and domain knowledge
    3. Soft skills and cultural fit requirements
    4. Preferred qualifications and nice-to-haves
    """

    response = await llm.ainvoke(analysis_prompt)

    return {
        **state,
        "job_analysis": parse_job_analysis(response)
    }

async def search_matching_candidates(state: CandidateAnalysisState) -> CandidateAnalysisState:
    """Search for candidates matching job requirements"""
    job_analysis = state["job_analysis"]

    # Generate search query from job analysis
    search_query = generate_candidate_search_query(job_analysis)

    # Search vector database
    candidate_matches = await vector_db.search(
        collection_name="candidates",
        query_vector=generate_embedding(search_query),
        limit=50
    )

    # Filter and enrich candidate data
    enriched_candidates = await enrich_candidate_data(candidate_matches)

    return {
        **state,
        "candidate_matches": enriched_candidates
    }

async def evaluate_candidate_profiles(state: CandidateAnalysisState) -> CandidateAnalysisState:
    """Evaluate candidate profiles against job requirements"""
    job_analysis = state["job_analysis"]
    candidate_matches = state["candidate_matches"]

    # Evaluate each candidate
    evaluated_candidates = []
    for candidate in candidate_matches:
        evaluation = await evaluate_candidate(job_analysis, candidate)
        evaluated_candidates.append({
            **candidate,
            "evaluation": evaluation,
            "match_score": evaluation["overall_score"]
        })

    # Sort by match score
    evaluated_candidates.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        **state,
        "evaluated_candidates": evaluated_candidates[:10]  # Top 10 candidates
    }

async def evaluate_candidate(job_analysis: dict, candidate: dict) -> dict:
    """Evaluate a single candidate against job requirements"""
    evaluation_prompt = f"""
    Evaluate the following candidate against the job requirements:

    Job Requirements: {job_analysis}
    Candidate Profile: {candidate}

    Provide evaluation on:
    1. Technical skills match (0-100)
    2. Experience relevance (0-100)
    3. Cultural fit potential (0-100)
    4. Overall suitability (0-100)
    5. Strengths and weaknesses
    6. Recommendations for consideration
    """

    response = await llm.ainvoke(evaluation_prompt)
    return parse_evaluation_response(response)
```

## Vector Database Integration

### Qdrant Client

```python
# common/vector_db.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from typing import List, Dict, Any

class VectorDatabase:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def create_collection(self, collection_name: str, vector_size: int = 384):
        """Create a new collection"""
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

    async def add_jobs(self, jobs: List[Dict[str, Any]]):
        """Add jobs to vector database"""
        points = []
        for job in jobs:
            # Generate embedding from job description
            text = f"{job['title']} {job['company']} {job['description']} {' '.join(job['requirements'])}"
            embedding = self.embedding_model.encode(text)

            points.append(PointStruct(
                id=job['id'],
                vector=embedding.tolist(),
                payload={
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'description': job['description'],
                    'requirements': job['requirements'],
                    'job_type': job['job_type'],
                    'experience_level': job['experience_level']
                }
            ))

        self.client.upsert(
            collection_name="jobs",
            points=points
        )

    async def add_candidates(self, candidates: List[Dict[str, Any]]):
        """Add candidates to vector database"""
        points = []
        for candidate in candidates:
            # Generate embedding from candidate profile
            text = f"{candidate['headline']} {candidate['summary']} {' '.join(candidate['skills'])}"
            embedding = self.embedding_model.encode(text)

            points.append(PointStruct(
                id=candidate['id'],
                vector=embedding.tolist(),
                payload={
                    'headline': candidate['headline'],
                    'summary': candidate['summary'],
                    'skills': candidate['skills'],
                    'experience_years': candidate['experience_years'],
                    'education': candidate['education']
                }
            ))

        self.client.upsert(
            collection_name="candidates",
            points=points
        )

    async def search_jobs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for jobs using vector similarity"""
        query_embedding = self.embedding_model.encode(query)

        results = self.client.search(
            collection_name="jobs",
            query_vector=query_embedding.tolist(),
            limit=limit
        )

        return [result.payload for result in results]

    async def search_candidates(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for candidates using vector similarity"""
        query_embedding = self.embedding_model.encode(query)

        results = self.client.search(
            collection_name="candidates",
            query_vector=query_embedding.tolist(),
            limit=limit
        )

        return [result.payload for result in results]
```

## Communication Protocols

### A2A Protocol (Agent-to-Agent)

```python
# common/a2a_protocol.py
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from kafka import KafkaProducer, KafkaConsumer
import asyncio

class A2AProtocol:
    def __init__(self, agent_id: str, kafka_config: Dict[str, Any]):
        self.agent_id = agent_id
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            'a2a-requests',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id=f"{agent_id}-consumer"
        )
        self.pending_requests = {}

    async def send_request(self, target_agent: str, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to another agent"""
        request_id = str(uuid.uuid4())

        message = {
            'request_id': request_id,
            'from_agent': self.agent_id,
            'to_agent': target_agent,
            'request_type': request_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Send request
        await self.producer.send('a2a-requests', message)

        # Wait for response
        response = await self.wait_for_response(request_id)
        return response

    async def wait_for_response(self, request_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for response to a specific request"""
        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).seconds < timeout:
            for message in self.consumer:
                if message.value['request_id'] == request_id:
                    return message.value['response']

            await asyncio.sleep(0.1)

        raise TimeoutError(f"Response timeout for request {request_id}")

    async def handle_incoming_requests(self, request_handler):
        """Handle incoming requests from other agents"""
        for message in self.consumer:
            request = message.value

            if request['to_agent'] == self.agent_id:
                # Process request
                response = await request_handler(request)

                # Send response
                response_message = {
                    'request_id': request['request_id'],
                    'from_agent': self.agent_id,
                    'to_agent': request['from_agent'],
                    'response': response,
                    'timestamp': datetime.utcnow().isoformat()
                }

                await self.producer.send('a2a-responses', response_message)

# Example usage
async def handle_candidate_analysis_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle candidate analysis request from job finder agent"""
    candidate_id = request['data']['candidate_id']

    # Analyze candidate
    analysis = await analyze_candidate_profile(candidate_id)

    return {
        'candidate_id': candidate_id,
        'analysis': analysis,
        'recommendations': generate_recommendations(analysis)
    }
```

### HTTP API Server

```python
# job_finder_agent/http_server.py
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, Any

app = FastAPI(title="Job Finder Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = JobFinderAgent(config)

@app.post("/chat")
async def chat_with_agent(request: Dict[str, Any]):
    """Chat with the job finder agent"""
    try:
        response = await agent.process_request(request)
        return {
            "success": True,
            "data": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            request = json.loads(data)

            # Process with agent
            response = await agent.process_request(request)

            # Send response
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "error": str(e)
        }))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_type": "job-finder",
        "timestamp": datetime.utcnow().isoformat()
    }
```

## MCP Tools Integration

### MCP Client

```python
# common/mcp_client.py
import aiohttp
from typing import Dict, Any, List
import json

class MCPClient:
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
        self.session = aiohttp.ClientSession()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        async with self.session.get(f"{self.mcp_server_url}/tools") as response:
            return await response.json()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }

        async with self.session.post(
            f"{self.mcp_server_url}/call",
            json=payload
        ) as response:
            return await response.json()

    async def github_analyze_profile(self, username: str) -> Dict[str, Any]:
        """Analyze GitHub profile using MCP tool"""
        return await self.call_tool("github_analyze_profile", {
            "username": username
        })

    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using MCP tool"""
        return await self.call_tool("send_email", {
            "to": to,
            "subject": subject,
            "body": body
        })

    async def schedule_interview(self, candidate_email: str, job_title: str, date: str) -> Dict[str, Any]:
        """Schedule interview using MCP tool"""
        return await self.call_tool("schedule_interview", {
            "candidate_email": candidate_email,
            "job_title": job_title,
            "date": date
        })

# Example usage in agent
async def analyze_candidate_portfolio(candidate_id: str) -> Dict[str, Any]:
    """Analyze candidate portfolio using MCP tools"""
    mcp_client = MCPClient(config.mcp_server_url)

    # Get candidate data
    candidate = await get_candidate_profile(candidate_id)

    # Analyze GitHub profile if available
    if candidate.get('github_url'):
        github_username = extract_github_username(candidate['github_url'])
        github_analysis = await mcp_client.github_analyze_profile(github_username)
    else:
        github_analysis = None

    # Analyze LinkedIn profile if available
    if candidate.get('linkedin_url'):
        linkedin_analysis = await mcp_client.call_tool("linkedin_analyze_profile", {
            "profile_url": candidate['linkedin_url']
        })
    else:
        linkedin_analysis = None

    return {
        'candidate_id': candidate_id,
        'github_analysis': github_analysis,
        'linkedin_analysis': linkedin_analysis,
        'overall_assessment': generate_overall_assessment(github_analysis, linkedin_analysis)
    }
```

## API Design

### Agent API Endpoints

```python
# API endpoints for job finder agent
@app.post("/api/v1/job-finder/chat")
async def chat_with_job_finder(request: JobFinderRequest):
    """Chat with job finder agent"""
    response = await agent.process_request(request)
    return JobFinderResponse(**response)

@app.post("/api/v1/job-finder/match-jobs")
async def match_jobs(request: JobMatchingRequest):
    """Get job matches for a candidate"""
    matches = await agent.match_jobs(request.candidate_id, request.preferences)
    return JobMatchingResponse(matches=matches)

@app.post("/api/v1/job-finder/apply-job")
async def apply_for_job(request: JobApplicationRequest):
    """Apply for a job with agent assistance"""
    application = await agent.apply_for_job(
        request.candidate_id,
        request.job_id,
        request.cover_letter
    )
    return JobApplicationResponse(**application)

# API endpoints for candidate finder agent
@app.post("/api/v1/candidate-finder/chat")
async def chat_with_candidate_finder(request: CandidateFinderRequest):
    """Chat with candidate finder agent"""
    response = await agent.process_request(request)
    return CandidateFinderResponse(**response)

@app.post("/api/v1/candidate-finder/find-candidates")
async def find_candidates(request: CandidateSearchRequest):
    """Find candidates for a job"""
    candidates = await agent.find_candidates(request.job_id, request.criteria)
    return CandidateSearchResponse(candidates=candidates)

@app.post("/api/v1/candidate-finder/evaluate-candidate")
async def evaluate_candidate(request: CandidateEvaluationRequest):
    """Evaluate a specific candidate"""
    evaluation = await agent.evaluate_candidate(
        request.candidate_id,
        request.job_id
    )
    return CandidateEvaluationResponse(**evaluation)
```

### Request/Response Models

```python
# Pydantic models for API requests and responses
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobFinderRequest(BaseModel):
    candidate_id: str
    message: str
    preferences: Optional[Dict[str, Any]] = None

class JobFinderResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    reasoning: str
    next_steps: List[str]
    timestamp: datetime

class JobMatchingRequest(BaseModel):
    candidate_id: str
    preferences: Dict[str, Any]
    limit: Optional[int] = 10

class JobMatchingResponse(BaseModel):
    matches: List[Dict[str, Any]]
    total_count: int
    match_scores: Dict[str, float]

class CandidateFinderRequest(BaseModel):
    job_id: str
    message: str
    criteria: Optional[Dict[str, Any]] = None

class CandidateFinderResponse(BaseModel):
    candidates: List[Dict[str, Any]]
    reasoning: str
    next_steps: List[str]
    timestamp: datetime

class CandidateSearchRequest(BaseModel):
    job_id: str
    criteria: Dict[str, Any]
    limit: Optional[int] = 10

class CandidateSearchResponse(BaseModel):
    candidates: List[Dict[str, Any]]
    total_count: int
    match_scores: Dict[str, float]
```

## Testing Strategy

### Unit Testing

```python
# tests/test_job_finder_agent.py
import pytest
from unittest.mock import Mock, AsyncMock
from job_finder_agent.main import JobFinderAgent
from job_finder_agent.workflows.match_jobs import create_job_matching_workflow

class TestJobFinderAgent:
    @pytest.fixture
    def agent(self):
        config = Mock()
        config.openai_api_key = "test-key"
        config.vector_db_url = "http://localhost:6333"
        return JobFinderAgent(config)

    @pytest.fixture
    def mock_llm(self):
        return AsyncMock()

    @pytest.fixture
    def mock_vector_db(self):
        return AsyncMock()

    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.config is not None
        assert agent.workflow is not None

    @pytest.mark.asyncio
    async def test_process_request(self, agent, mock_llm, mock_vector_db):
        """Test processing a job search request"""
        # Mock dependencies
        agent.llm = mock_llm
        agent.vector_db = mock_vector_db

        # Mock workflow execution
        agent.workflow.ainvoke = AsyncMock(return_value={
            'recommendations': [{'id': '1', 'title': 'Software Engineer'}],
            'reasoning': 'Good match based on skills',
            'next_steps': ['Apply for the job']
        })

        # Test request
        request = {
            'candidate_id': 'test-candidate',
            'message': 'Find me a job',
            'preferences': {'location': 'San Francisco'}
        }

        response = await agent.process_request(request)

        assert response['recommendations'] is not None
        assert response['reasoning'] is not None
        assert response['next_steps'] is not None

class TestJobMatchingWorkflow:
    @pytest.mark.asyncio
    async def test_analyze_profile(self):
        """Test profile analysis workflow node"""
        workflow = create_job_matching_workflow()

        state = {
            'candidate_id': 'test-candidate',
            'preferences': {},
            'message': 'Find me a job'
        }

        # Mock get_candidate_profile
        with patch('job_finder_agent.workflows.match_jobs.get_candidate_profile') as mock_get:
            mock_get.return_value = {
                'skills': ['Python', 'Go'],
                'experience': '5 years',
                'education': 'BS Computer Science'
            }

            result = await workflow.ainvoke(state)

            assert 'profile_analysis' in result
            assert result['profile_analysis'] is not None

    @pytest.mark.asyncio
    async def test_search_jobs(self):
        """Test job search workflow node"""
        workflow = create_job_matching_workflow()

        state = {
            'candidate_id': 'test-candidate',
            'preferences': {},
            'message': 'Find me a job',
            'profile_analysis': {
                'skills': ['Python', 'Go'],
                'experience_level': 'senior'
            }
        }

        # Mock vector database search
        with patch('job_finder_agent.workflows.match_jobs.vector_db.search') as mock_search:
            mock_search.return_value = [
                {'id': '1', 'title': 'Senior Python Developer'},
                {'id': '2', 'title': 'Go Backend Engineer'}
            ]

            result = await workflow.ainvoke(state)

            assert 'job_matches' in result
            assert len(result['job_matches']) > 0
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
import asyncio
from httpx import AsyncClient
from job_finder_agent.http_server import app

class TestAgentAPI:
    @pytest.mark.asyncio
    async def test_chat_endpoint(self):
        """Test chat endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chat", json={
                "candidate_id": "test-candidate",
                "message": "Find me a job in San Francisco",
                "preferences": {
                    "location": "San Francisco",
                    "job_type": "full-time"
                }
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with ac.websocket_connect("/ws") as websocket:
                # Send message
                await websocket.send_json({
                    "candidate_id": "test-candidate",
                    "message": "Hello agent"
                })

                # Receive response
                response = await websocket.receive_json()
                assert "response" in response or "error" in response
```

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8084

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8084/health || exit 1

# Run application
CMD ["python", "job_finder_agent/http_server.py"]
```

### Environment Configuration

```bash
# .env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Vector Database
VECTOR_DB_URL=http://qdrant:6333

# Kafka Configuration
KAFKA_BROKERS=kafka:9092
KAFKA_TOPIC_PREFIX=jobzee

# Agent Configuration
AGENT_TYPE=job-finder
AGENT_PORT=8084
AGENT_HTTP_HOST=0.0.0.0

# MCP Tools
MCP_SERVER_URL=http://mcp-tools:8086

# Backend API
BACKEND_API_URL=http://api-service:8080/api/v1

# Logging
LOG_LEVEL=info
```

### Kubernetes Deployment

```yaml
# kubernetes/job-finder-agent.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: job-finder-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: job-finder-agent
  template:
    metadata:
      labels:
        app: job-finder-agent
    spec:
      containers:
        - name: job-finder-agent
          image: jobzee/job-finder-agent:latest
          ports:
            - containerPort: 8084
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: OPENAI_API_KEY
            - name: VECTOR_DB_URL
              value: "http://qdrant:6333"
            - name: KAFKA_BROKERS
              value: "kafka:9092"
          livenessProbe:
            httpGet:
              path: /health
              port: 8084
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8084
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: job-finder-agent
spec:
  selector:
    app: job-finder-agent
  ports:
    - protocol: TCP
      port: 8084
      targetPort: 8084
  type: ClusterIP
```

---

## Conclusion

The JobZee Agents repository provides:

- **Intelligent Automation**: AI-powered agents for job matching and recruitment
- **Scalable Architecture**: LangGraph workflows for complex business logic
- **Vector Search**: Semantic search using Qdrant for intelligent matching
- **Real-time Communication**: WebSocket and HTTP APIs for seamless interaction
- **Tool Integration**: MCP protocol for external tool access
- **Comprehensive Testing**: Unit and integration tests for reliability
- **Production Ready**: Docker and Kubernetes deployment configurations

The agents serve as the intelligent core of the JobZee platform, providing sophisticated job matching and recruitment automation capabilities.
