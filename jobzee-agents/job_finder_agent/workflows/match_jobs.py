"""
Job Finder Agent - Job Matching Workflow

This workflow matches jobs with candidates using vector similarity
and AI-powered analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
import asyncio

from common.mcp_client import MCPClient, ToolType
from common.vector_db import VectorDatabase
from common.a2a_protocol import AgentToAgentProtocol, MessageType, MatchRequest, MatchResponse

logger = logging.getLogger(__name__)


@dataclass
class JobMatch:
    """Represents a job match for a candidate."""
    
    job_id: str
    job_title: str
    company: str
    location: str
    match_score: float
    reasoning: str
    skills_match: List[str]
    missing_skills: List[str]
    salary_range: Optional[str] = None
    job_type: str = "full-time"
    remote_friendly: bool = False


class MatchingState(BaseModel):
    """State for job matching workflow."""
    
    candidate_id: str
    candidate_profile: Dict[str, Any] = {}
    available_jobs: List[Dict[str, Any]] = []
    matches: List[JobMatch] = []
    current_job_index: int = 0
    is_complete: bool = False
    error_message: str = ""
    
    # Matching criteria
    min_match_score: float = 0.7
    max_matches: int = 10
    required_skills_weight: float = 0.4
    experience_weight: float = 0.3
    location_weight: float = 0.2
    salary_weight: float = 0.1


class JobMatcher:
    """Matches jobs with candidates using AI and vector similarity."""
    
    def __init__(self, mcp_client: MCPClient, vector_db: VectorDatabase, a2a_protocol: AgentToAgentProtocol):
        self.mcp_client = mcp_client
        self.vector_db = vector_db
        self.a2a_protocol = a2a_protocol
    
    async def load_candidate_profile(self, state: MatchingState) -> MatchingState:
        """Load candidate profile from vector database."""
        try:
            # Get candidate profile from vector DB
            profile = await self.vector_db.get_document(
                collection_name="candidates",
                document_id=state.candidate_id
            )
            
            if profile:
                state.candidate_profile = profile.metadata
                logger.info(f"Loaded profile for candidate {state.candidate_id}")
            else:
                logger.warning(f"No profile found for candidate {state.candidate_id}")
                state.error_message = "Candidate profile not found"
            
        except Exception as e:
            logger.error(f"Error loading candidate profile: {e}")
            state.error_message = str(e)
        
        return state
    
    async def search_available_jobs(self, state: MatchingState) -> MatchingState:
        """Search for available jobs using vector similarity."""
        try:
            if not state.candidate_profile:
                logger.warning("No candidate profile available for job search")
                return state
            
            # Create search query from candidate profile
            search_query = self._create_search_query(state.candidate_profile)
            
            # Search for similar jobs in vector database
            search_results = await self.vector_db.search(
                collection_name="jobs",
                query=search_query,
                limit=50,  # Get more results for filtering
                filter_criteria={
                    "status": "active",
                    "remote_friendly": state.candidate_profile.get("remote_preference", True)
                }
            )
            
            state.available_jobs = [
                {
                    "id": result.document_id,
                    "metadata": result.metadata,
                    "score": result.score
                }
                for result in search_results
            ]
            
            logger.info(f"Found {len(state.available_jobs)} potential jobs for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            state.error_message = str(e)
        
        return state
    
    def _create_search_query(self, profile: Dict[str, Any]) -> str:
        """Create search query from candidate profile."""
        skills = profile.get("skills", [])
        preferred_roles = profile.get("preferred_roles", [])
        experience_years = profile.get("experience_years", 0)
        
        query_parts = []
        
        if skills:
            query_parts.append(f"Skills: {', '.join(skills)}")
        
        if preferred_roles:
            query_parts.append(f"Roles: {', '.join(preferred_roles)}")
        
        if experience_years:
            query_parts.append(f"Experience: {experience_years} years")
        
        return " ".join(query_parts)
    
    async def analyze_job_match(self, state: MatchingState, job_data: Dict[str, Any]) -> JobMatch:
        """Analyze match between candidate and job using AI."""
        try:
            candidate_skills = set(state.candidate_profile.get("skills", []))
            job_skills = set(job_data["metadata"].get("skills", []))
            
            # Calculate basic matching metrics
            skills_match = list(candidate_skills.intersection(job_skills))
            missing_skills = list(job_skills - candidate_skills)
            
            # Calculate match score
            match_score = self._calculate_match_score(
                state.candidate_profile,
                job_data["metadata"],
                skills_match,
                missing_skills
            )
            
            # Generate reasoning using AI
            reasoning = await self._generate_match_reasoning(
                state.candidate_profile,
                job_data["metadata"],
                skills_match,
                missing_skills,
                match_score
            )
            
            return JobMatch(
                job_id=job_data["id"],
                job_title=job_data["metadata"].get("title", ""),
                company=job_data["metadata"].get("company", ""),
                location=job_data["metadata"].get("location", ""),
                match_score=match_score,
                reasoning=reasoning,
                skills_match=skills_match,
                missing_skills=missing_skills,
                salary_range=job_data["metadata"].get("salary_range"),
                job_type=job_data["metadata"].get("job_type", "full-time"),
                remote_friendly=job_data["metadata"].get("remote_friendly", False)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing job match: {e}")
            # Return a basic match with error
            return JobMatch(
                job_id=job_data["id"],
                job_title=job_data["metadata"].get("title", ""),
                company=job_data["metadata"].get("company", ""),
                location=job_data["metadata"].get("location", ""),
                match_score=0.0,
                reasoning=f"Error analyzing match: {str(e)}",
                skills_match=[],
                missing_skills=[]
            )
    
    def _calculate_match_score(self, candidate_profile: Dict[str, Any], 
                             job_data: Dict[str, Any], skills_match: List[str], 
                             missing_skills: List[str]) -> float:
        """Calculate match score between candidate and job."""
        try:
            # Skills match score (40% weight)
            candidate_skills = set(candidate_profile.get("skills", []))
            job_skills = set(job_data.get("skills", []))
            
            if not job_skills:
                skills_score = 0.0
            else:
                skills_score = len(skills_match) / len(job_skills)
            
            # Experience match score (30% weight)
            candidate_exp = candidate_profile.get("experience_years", 0)
            job_exp_min = self._extract_min_experience(job_data.get("experience_level", ""))
            job_exp_max = self._extract_max_experience(job_data.get("experience_level", ""))
            
            if job_exp_min <= candidate_exp <= job_exp_max:
                exp_score = 1.0
            elif candidate_exp < job_exp_min:
                exp_score = max(0.0, 1.0 - (job_exp_min - candidate_exp) / 5.0)
            else:
                exp_score = max(0.0, 1.0 - (candidate_exp - job_exp_max) / 5.0)
            
            # Location match score (20% weight)
            candidate_location = candidate_profile.get("location", "").lower()
            job_location = job_data.get("location", "").lower()
            
            if candidate_location in job_location or job_location in candidate_location:
                location_score = 1.0
            elif candidate_profile.get("remote_preference", False) and job_data.get("remote_friendly", False):
                location_score = 0.8
            else:
                location_score = 0.0
            
            # Salary match score (10% weight)
            salary_score = self._calculate_salary_match(
                candidate_profile.get("salary_expectation", ""),
                job_data.get("salary_range", "")
            )
            
            # Calculate weighted score
            total_score = (
                skills_score * 0.4 +
                exp_score * 0.3 +
                location_score * 0.2 +
                salary_score * 0.1
            )
            
            return min(1.0, max(0.0, total_score))
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0.0
    
    def _extract_min_experience(self, experience_level: str) -> int:
        """Extract minimum years from experience level."""
        mappings = {
            "entry": 0,
            "junior": 0,
            "mid": 3,
            "senior": 5,
            "lead": 8,
            "principal": 12
        }
        return mappings.get(experience_level.lower(), 0)
    
    def _extract_max_experience(self, experience_level: str) -> int:
        """Extract maximum years from experience level."""
        mappings = {
            "entry": 2,
            "junior": 2,
            "mid": 5,
            "senior": 8,
            "lead": 12,
            "principal": 20
        }
        return mappings.get(experience_level.lower(), 5)
    
    def _calculate_salary_match(self, candidate_salary: str, job_salary: str) -> float:
        """Calculate salary match score."""
        try:
            # Simple salary matching - in production, use proper salary parsing
            if not candidate_salary or not job_salary:
                return 0.5  # Neutral score if salary info is missing
            
            # Extract numbers from salary strings
            import re
            candidate_numbers = [int(x) for x in re.findall(r'\d+', candidate_salary)]
            job_numbers = [int(x) for x in re.findall(r'\d+', job_salary)]
            
            if not candidate_numbers or not job_numbers:
                return 0.5
            
            candidate_avg = sum(candidate_numbers) / len(candidate_numbers)
            job_avg = sum(job_numbers) / len(job_numbers)
            
            # Calculate overlap
            if job_avg > 0:
                ratio = candidate_avg / job_avg
                if 0.8 <= ratio <= 1.2:
                    return 1.0
                elif 0.6 <= ratio <= 1.4:
                    return 0.7
                else:
                    return 0.3
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating salary match: {e}")
            return 0.5
    
    async def _generate_match_reasoning(self, candidate_profile: Dict[str, Any], 
                                      job_data: Dict[str, Any], skills_match: List[str], 
                                      missing_skills: List[str], match_score: float) -> str:
        """Generate AI-powered reasoning for the match."""
        try:
            # Create prompt for reasoning generation
            prompt = f"""
            Analyze the match between a candidate and a job posting:
            
            Candidate Profile:
            - Skills: {', '.join(candidate_profile.get('skills', []))}
            - Experience: {candidate_profile.get('experience_years', 0)} years
            - Preferred Roles: {', '.join(candidate_profile.get('preferred_roles', []))}
            
            Job Details:
            - Title: {job_data.get('title', '')}
            - Company: {job_data.get('company', '')}
            - Required Skills: {', '.join(job_data.get('skills', []))}
            - Experience Level: {job_data.get('experience_level', '')}
            
            Match Analysis:
            - Matching Skills: {', '.join(skills_match)}
            - Missing Skills: {', '.join(missing_skills)}
            - Match Score: {match_score:.2f}
            
            Provide a brief, professional explanation of why this is a good match or not.
            Focus on skills alignment, experience fit, and growth opportunities.
            """
            
            # Use MCP to generate reasoning (simplified for now)
            if match_score >= 0.8:
                reasoning = f"Excellent match! The candidate has {len(skills_match)} out of {len(job_data.get('skills', []))} required skills. "
                if skills_match:
                    reasoning += f"Strong alignment in: {', '.join(skills_match[:3])}. "
                if missing_skills:
                    reasoning += f"Could learn: {', '.join(missing_skills[:2])}. "
                reasoning += "Experience level and role preferences align well."
            elif match_score >= 0.6:
                reasoning = f"Good match with {len(skills_match)} matching skills. "
                if missing_skills:
                    reasoning += f"Would need to develop: {', '.join(missing_skills[:3])}. "
                reasoning += "Experience level is appropriate for the role."
            else:
                reasoning = f"Limited match with only {len(skills_match)} matching skills. "
                if missing_skills:
                    reasoning += f"Significant skill gaps: {', '.join(missing_skills[:3])}. "
                reasoning += "May not be the best fit for this position."
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return f"Match score: {match_score:.2f}. Analysis unavailable."
    
    async def process_job_matches(self, state: MatchingState) -> MatchingState:
        """Process all available jobs and create matches."""
        try:
            matches = []
            
            for job_data in state.available_jobs:
                if len(matches) >= state.max_matches:
                    break
                
                match = await self.analyze_job_match(state, job_data)
                
                # Only include matches above threshold
                if match.match_score >= state.min_match_score:
                    matches.append(match)
            
            # Sort by match score
            matches.sort(key=lambda x: x.match_score, reverse=True)
            state.matches = matches
            
            logger.info(f"Created {len(matches)} matches for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error processing job matches: {e}")
            state.error_message = str(e)
        
        return state
    
    async def notify_candidate_finder(self, state: MatchingState) -> MatchingState:
        """Notify candidate finder agent about potential matches."""
        try:
            if not state.matches:
                return state
            
            # Create match request for candidate finder
            match_request = MatchRequest(
                request_id=f"match_{state.candidate_id}_{len(state.matches)}",
                candidate_id=state.candidate_id,
                criteria={
                    "min_match_score": state.min_match_score,
                    "max_matches": state.max_matches,
                    "candidate_profile": state.candidate_profile
                }
            )
            
            # Send to candidate finder agent
            await self.a2a_protocol.send_match_request(
                receiver_id="candidate_finder_agent",
                match_request=match_request
            )
            
            logger.info(f"Sent match request to candidate finder for {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error notifying candidate finder: {e}")
            state.error_message = str(e)
        
        return state


def create_job_matching_graph(mcp_client: MCPClient, vector_db: VectorDatabase, a2a_protocol: AgentToAgentProtocol):
    """Create the LangGraph for job matching."""
    
    matcher = JobMatcher(mcp_client, vector_db, a2a_protocol)
    
    # Define the state graph
    workflow = StateGraph(MatchingState)
    
    # Add nodes
    workflow.add_node("load_profile", lambda state: matcher.load_candidate_profile(state))
    workflow.add_node("search_jobs", lambda state: matcher.search_available_jobs(state))
    workflow.add_node("process_matches", lambda state: matcher.process_job_matches(state))
    workflow.add_node("notify_finder", lambda state: matcher.notify_candidate_finder(state))
    
    # Define edges
    workflow.set_entry_point("load_profile")
    workflow.add_edge("load_profile", "search_jobs")
    workflow.add_edge("search_jobs", "process_matches")
    workflow.add_edge("process_matches", "notify_finder")
    workflow.add_edge("notify_finder", END)
    
    return workflow.compile()


async def run_job_matching(candidate_id: str, matching_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run the job matching workflow."""
    
    # Initialize components
    mcp_client = MCPClient()
    vector_db = VectorDatabase()
    a2a_protocol = AgentToAgentProtocol(kafka_client=None, agent_id="job_finder_agent")
    
    # Create initial state
    initial_state = MatchingState(
        candidate_id=candidate_id
    )
    
    if matching_criteria:
        initial_state.min_match_score = matching_criteria.get("min_match_score", 0.7)
        initial_state.max_matches = matching_criteria.get("max_matches", 10)
    
    # Create and run workflow
    graph = create_job_matching_graph(mcp_client, vector_db, a2a_protocol)
    
    try:
        result = await graph.ainvoke(initial_state)
        return {
            "success": True,
            "candidate_id": candidate_id,
            "matches": [
                {
                    "job_id": match.job_id,
                    "job_title": match.job_title,
                    "company": match.company,
                    "location": match.location,
                    "match_score": match.match_score,
                    "reasoning": match.reasoning,
                    "skills_match": match.skills_match,
                    "missing_skills": match.missing_skills,
                    "salary_range": match.salary_range,
                    "job_type": match.job_type,
                    "remote_friendly": match.remote_friendly
                }
                for match in result.matches
            ],
            "total_matches": len(result.matches)
        }
    except Exception as e:
        logger.error(f"Error in job matching: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        await mcp_client.close()
        vector_db.close() 