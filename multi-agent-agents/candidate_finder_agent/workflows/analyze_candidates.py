"""
Candidate Finder Agent - Candidate Analysis Workflow

This workflow analyzes candidates using MCP tools for portfolio analysis,
resume parsing, and comprehensive candidate assessment.
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
class CandidateAnalysis:
    """Represents a comprehensive candidate analysis."""
    
    candidate_id: str
    overall_score: float
    skills_assessment: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    portfolio_evaluation: Dict[str, Any]
    cultural_fit: Dict[str, Any]
    recommendations: List[str]
    risk_factors: List[str]
    interview_questions: List[str]
    technical_assessment: Dict[str, Any] = None


class AnalysisState(BaseModel):
    """State for candidate analysis workflow."""
    
    candidate_id: str
    job_requirements: Dict[str, Any] = {}
    candidate_profile: Dict[str, Any] = {}
    analysis_results: Dict[str, Any] = {}
    current_step: str = "load_profile"
    is_complete: bool = False
    error_message: str = ""
    
    # Analysis components
    skills_analysis: Dict[str, Any] = {}
    experience_analysis: Dict[str, Any] = {}
    portfolio_analysis: Dict[str, Any] = {}
    cultural_fit_analysis: Dict[str, Any] = {}
    technical_assessment: Dict[str, Any] = {}


class CandidateAnalyzer:
    """Analyzes candidates using MCP tools and AI assessment."""
    
    def __init__(self, mcp_client: MCPClient, vector_db: VectorDatabase, a2a_protocol: AgentToAgentProtocol):
        self.mcp_client = mcp_client
        self.vector_db = vector_db
        self.a2a_protocol = a2a_protocol
    
    async def load_candidate_profile(self, state: AnalysisState) -> AnalysisState:
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
    
    async def analyze_skills(self, state: AnalysisState) -> AnalysisState:
        """Analyze candidate skills against job requirements."""
        try:
            candidate_skills = set(state.candidate_profile.get("skills", []))
            required_skills = set(state.job_requirements.get("skills", []))
            
            # Calculate skill metrics
            matching_skills = list(candidate_skills.intersection(required_skills))
            missing_skills = list(required_skills - candidate_skills)
            additional_skills = list(candidate_skills - required_skills)
            
            # Calculate skill coverage
            skill_coverage = len(matching_skills) / len(required_skills) if required_skills else 0.0
            
            # Assess skill levels (simplified - in production, use more sophisticated analysis)
            skill_levels = {}
            for skill in matching_skills:
                # This would typically use AI to assess skill proficiency
                skill_levels[skill] = {
                    "level": "proficient",  # beginner, intermediate, proficient, expert
                    "confidence": 0.8,
                    "evidence": "Based on experience and portfolio"
                }
            
            state.skills_analysis = {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "additional_skills": additional_skills,
                "skill_coverage": skill_coverage,
                "skill_levels": skill_levels,
                "overall_skill_score": min(1.0, skill_coverage * 1.2)  # Bonus for additional skills
            }
            
            logger.info(f"Completed skills analysis for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing skills: {e}")
            state.error_message = str(e)
        
        return state
    
    async def analyze_experience(self, state: AnalysisState) -> AnalysisState:
        """Analyze candidate experience against job requirements."""
        try:
            candidate_exp = state.candidate_profile.get("experience_years", 0)
            required_exp_min = self._extract_min_experience(state.job_requirements.get("experience_level", ""))
            required_exp_max = self._extract_max_experience(state.job_requirements.get("experience_level", ""))
            
            # Experience fit analysis
            if required_exp_min <= candidate_exp <= required_exp_max:
                exp_fit_score = 1.0
                exp_assessment = "excellent"
            elif candidate_exp < required_exp_min:
                exp_fit_score = max(0.0, 1.0 - (required_exp_min - candidate_exp) / 5.0)
                exp_assessment = "below_required"
            else:
                exp_fit_score = max(0.0, 1.0 - (candidate_exp - required_exp_max) / 5.0)
                exp_assessment = "overqualified"
            
            # Analyze work experience details
            work_experience = state.candidate_profile.get("work_experience", [])
            relevant_experience = []
            
            for exp in work_experience:
                # Check if experience is relevant to job requirements
                relevance_score = self._calculate_experience_relevance(exp, state.job_requirements)
                if relevance_score > 0.5:
                    relevant_experience.append({
                        "experience": exp,
                        "relevance_score": relevance_score
                    })
            
            state.experience_analysis = {
                "candidate_experience_years": candidate_exp,
                "required_experience_range": f"{required_exp_min}-{required_exp_max}",
                "experience_fit_score": exp_fit_score,
                "experience_assessment": exp_assessment,
                "relevant_experience": relevant_experience,
                "total_relevant_experience": len(relevant_experience)
            }
            
            logger.info(f"Completed experience analysis for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing experience: {e}")
            state.error_message = str(e)
        
        return state
    
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
    
    def _calculate_experience_relevance(self, experience: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """Calculate relevance of work experience to job requirements."""
        try:
            # Extract job title and description from experience
            job_title = experience.get("title", "").lower()
            job_description = experience.get("description", "").lower()
            
            # Extract required skills and role from job requirements
            required_skills = [skill.lower() for skill in job_requirements.get("skills", [])]
            required_role = job_requirements.get("title", "").lower()
            
            relevance_score = 0.0
            
            # Check title relevance
            if required_role and any(word in job_title for word in required_role.split()):
                relevance_score += 0.3
            
            # Check skills relevance
            skill_matches = sum(1 for skill in required_skills if skill in job_description)
            if required_skills:
                relevance_score += (skill_matches / len(required_skills)) * 0.7
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.error(f"Error calculating experience relevance: {e}")
            return 0.0
    
    async def analyze_portfolio(self, state: AnalysisState) -> AnalysisState:
        """Analyze candidate portfolio using MCP tools."""
        try:
            portfolio_links = state.candidate_profile.get("portfolio_links", [])
            portfolio_analysis = {}
            
            for link in portfolio_links:
                if "github.com" in link:
                    # Analyze GitHub profile
                    username = link.split("github.com/")[-1].split("/")[0]
                    response = await self.mcp_client.analyze_github_profile(username)
                    
                    if response.success:
                        portfolio_analysis["github"] = {
                            "username": username,
                            "analysis": response.result,
                            "score": self._calculate_github_score(response.result)
                        }
                
                elif "linkedin.com" in link:
                    # LinkedIn analysis placeholder
                    portfolio_analysis["linkedin"] = {
                        "profile_url": link,
                        "analysis": {"status": "analyzed"},
                        "score": 0.7  # Placeholder score
                    }
                
                elif "resume" in link.lower() or link.endswith(('.pdf', '.doc', '.docx')):
                    # Analyze resume
                    response = await self.mcp_client.parse_resume(link)
                    
                    if response.success:
                        portfolio_analysis["resume"] = {
                            "resume_url": link,
                            "analysis": response.result,
                            "score": self._calculate_resume_score(response.result)
                        }
            
            # Calculate overall portfolio score
            portfolio_scores = [analysis.get("score", 0.0) for analysis in portfolio_analysis.values()]
            overall_portfolio_score = sum(portfolio_scores) / len(portfolio_scores) if portfolio_scores else 0.0
            
            state.portfolio_analysis = {
                "portfolio_links": portfolio_links,
                "detailed_analysis": portfolio_analysis,
                "overall_portfolio_score": overall_portfolio_score,
                "portfolio_strengths": self._identify_portfolio_strengths(portfolio_analysis),
                "portfolio_weaknesses": self._identify_portfolio_weaknesses(portfolio_analysis)
            }
            
            logger.info(f"Completed portfolio analysis for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            state.error_message = str(e)
        
        return state
    
    def _calculate_github_score(self, github_analysis: Dict[str, Any]) -> float:
        """Calculate score based on GitHub analysis."""
        try:
            score = 0.0
            
            # Repository count
            repo_count = github_analysis.get("repository_count", 0)
            if repo_count >= 10:
                score += 0.3
            elif repo_count >= 5:
                score += 0.2
            elif repo_count >= 2:
                score += 0.1
            
            # Stars and forks
            total_stars = github_analysis.get("total_stars", 0)
            if total_stars >= 100:
                score += 0.3
            elif total_stars >= 20:
                score += 0.2
            elif total_stars >= 5:
                score += 0.1
            
            # Recent activity
            recent_commits = github_analysis.get("recent_commits", 0)
            if recent_commits >= 50:
                score += 0.2
            elif recent_commits >= 20:
                score += 0.15
            elif recent_commits >= 5:
                score += 0.1
            
            # Language diversity
            languages = github_analysis.get("languages", [])
            if len(languages) >= 3:
                score += 0.2
            elif len(languages) >= 2:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating GitHub score: {e}")
            return 0.0
    
    def _calculate_resume_score(self, resume_analysis: Dict[str, Any]) -> float:
        """Calculate score based on resume analysis."""
        try:
            score = 0.0
            
            # Experience length
            experience_years = resume_analysis.get("experience_years", 0)
            if experience_years >= 5:
                score += 0.3
            elif experience_years >= 3:
                score += 0.2
            elif experience_years >= 1:
                score += 0.1
            
            # Skills mentioned
            skills_count = len(resume_analysis.get("skills", []))
            if skills_count >= 10:
                score += 0.3
            elif skills_count >= 5:
                score += 0.2
            elif skills_count >= 2:
                score += 0.1
            
            # Education level
            education = resume_analysis.get("education", [])
            if any("phd" in edu.get("degree", "").lower() for edu in education):
                score += 0.2
            elif any("master" in edu.get("degree", "").lower() for edu in education):
                score += 0.15
            elif any("bachelor" in edu.get("degree", "").lower() for edu in education):
                score += 0.1
            
            # Certifications
            certifications = resume_analysis.get("certifications", [])
            if len(certifications) >= 3:
                score += 0.2
            elif len(certifications) >= 1:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating resume score: {e}")
            return 0.0
    
    def _identify_portfolio_strengths(self, portfolio_analysis: Dict[str, Any]) -> List[str]:
        """Identify strengths in the portfolio."""
        strengths = []
        
        for platform, analysis in portfolio_analysis.items():
            score = analysis.get("score", 0.0)
            
            if platform == "github" and score >= 0.7:
                strengths.append("Strong GitHub presence with active repositories")
            elif platform == "resume" and score >= 0.7:
                strengths.append("Well-structured resume with relevant experience")
            elif platform == "linkedin" and score >= 0.7:
                strengths.append("Professional LinkedIn profile")
        
        return strengths
    
    def _identify_portfolio_weaknesses(self, portfolio_analysis: Dict[str, Any]) -> List[str]:
        """Identify weaknesses in the portfolio."""
        weaknesses = []
        
        if not portfolio_analysis:
            weaknesses.append("No portfolio links provided")
            return weaknesses
        
        for platform, analysis in portfolio_analysis.items():
            score = analysis.get("score", 0.0)
            
            if platform == "github" and score < 0.5:
                weaknesses.append("Limited GitHub activity or repositories")
            elif platform == "resume" and score < 0.5:
                weaknesses.append("Resume could be more comprehensive")
            elif platform == "linkedin" and score < 0.5:
                weaknesses.append("LinkedIn profile needs improvement")
        
        return weaknesses
    
    async def assess_cultural_fit(self, state: AnalysisState) -> AnalysisState:
        """Assess cultural fit based on candidate profile and company requirements."""
        try:
            # This is a simplified cultural fit assessment
            # In production, this would use more sophisticated analysis
            
            cultural_fit_score = 0.7  # Base score
            
            # Adjust based on experience level
            candidate_exp = state.candidate_profile.get("experience_years", 0)
            required_exp = self._extract_min_experience(state.job_requirements.get("experience_level", ""))
            
            if candidate_exp >= required_exp:
                cultural_fit_score += 0.1
            
            # Adjust based on remote preference
            candidate_remote = state.candidate_profile.get("remote_preference", False)
            job_remote = state.job_requirements.get("remote_friendly", False)
            
            if candidate_remote == job_remote:
                cultural_fit_score += 0.1
            
            # Adjust based on location
            candidate_location = state.candidate_profile.get("location", "").lower()
            job_location = state.job_requirements.get("location", "").lower()
            
            if candidate_location in job_location or job_location in candidate_location:
                cultural_fit_score += 0.1
            
            state.cultural_fit_analysis = {
                "cultural_fit_score": min(1.0, cultural_fit_score),
                "experience_alignment": candidate_exp >= required_exp,
                "remote_preference_match": candidate_remote == job_remote,
                "location_compatibility": candidate_location in job_location or job_location in candidate_location,
                "recommendations": self._generate_cultural_fit_recommendations(state)
            }
            
            logger.info(f"Completed cultural fit analysis for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error assessing cultural fit: {e}")
            state.error_message = str(e)
        
        return state
    
    def _generate_cultural_fit_recommendations(self, state: AnalysisState) -> List[str]:
        """Generate recommendations for cultural fit improvement."""
        recommendations = []
        
        candidate_exp = state.candidate_profile.get("experience_years", 0)
        required_exp = self._extract_min_experience(state.job_requirements.get("experience_level", ""))
        
        if candidate_exp < required_exp:
            recommendations.append("Consider gaining more experience in the field")
        
        candidate_remote = state.candidate_profile.get("remote_preference", False)
        job_remote = state.job_requirements.get("remote_friendly", False)
        
        if candidate_remote != job_remote:
            recommendations.append("Consider flexibility in remote work preferences")
        
        return recommendations
    
    async def generate_final_assessment(self, state: AnalysisState) -> AnalysisState:
        """Generate final comprehensive assessment."""
        try:
            # Calculate overall score
            skill_score = state.skills_analysis.get("overall_skill_score", 0.0)
            experience_score = state.experience_analysis.get("experience_fit_score", 0.0)
            portfolio_score = state.portfolio_analysis.get("overall_portfolio_score", 0.0)
            cultural_score = state.cultural_fit_analysis.get("cultural_fit_score", 0.0)
            
            # Weighted overall score
            overall_score = (
                skill_score * 0.35 +
                experience_score * 0.25 +
                portfolio_score * 0.25 +
                cultural_score * 0.15
            )
            
            # Generate recommendations
            recommendations = []
            risk_factors = []
            
            # Skill-based recommendations
            missing_skills = state.skills_analysis.get("missing_skills", [])
            if missing_skills:
                recommendations.append(f"Consider developing skills in: {', '.join(missing_skills[:3])}")
                risk_factors.append(f"Missing key skills: {', '.join(missing_skills[:3])}")
            
            # Experience-based recommendations
            if state.experience_analysis.get("experience_assessment") == "below_required":
                recommendations.append("Consider gaining more relevant experience")
                risk_factors.append("Below required experience level")
            
            # Portfolio-based recommendations
            portfolio_weaknesses = state.portfolio_analysis.get("portfolio_weaknesses", [])
            if portfolio_weaknesses:
                recommendations.extend(portfolio_weaknesses[:2])
            
            # Generate interview questions
            interview_questions = self._generate_interview_questions(state)
            
            state.analysis_results = {
                "overall_score": overall_score,
                "skill_score": skill_score,
                "experience_score": experience_score,
                "portfolio_score": portfolio_score,
                "cultural_score": cultural_score,
                "recommendations": recommendations,
                "risk_factors": risk_factors,
                "interview_questions": interview_questions,
                "assessment_summary": self._generate_assessment_summary(state, overall_score)
            }
            
            state.is_complete = True
            logger.info(f"Completed final assessment for candidate {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error generating final assessment: {e}")
            state.error_message = str(e)
        
        return state
    
    def _generate_interview_questions(self, state: AnalysisState) -> List[str]:
        """Generate relevant interview questions based on analysis."""
        questions = []
        
        # Skills-based questions
        matching_skills = state.skills_analysis.get("matching_skills", [])
        if matching_skills:
            questions.append(f"Can you walk us through a project where you used {matching_skills[0]}?")
        
        # Experience-based questions
        relevant_experience = state.experience_analysis.get("relevant_experience", [])
        if relevant_experience:
            exp = relevant_experience[0]["experience"]
            questions.append(f"Tell us about your role as {exp.get('title', '')} at {exp.get('company', '')}")
        
        # Portfolio-based questions
        if state.portfolio_analysis.get("detailed_analysis", {}).get("github"):
            questions.append("Can you explain the architecture of your most complex GitHub project?")
        
        # Cultural fit questions
        questions.append("How do you prefer to work in a team environment?")
        questions.append("What are your career goals for the next 2-3 years?")
        
        return questions[:5]  # Limit to 5 questions
    
    def _generate_assessment_summary(self, state: AnalysisState, overall_score: float) -> str:
        """Generate a summary of the assessment."""
        if overall_score >= 0.8:
            summary = "Excellent candidate with strong alignment to job requirements."
        elif overall_score >= 0.6:
            summary = "Good candidate with solid qualifications and some areas for growth."
        elif overall_score >= 0.4:
            summary = "Moderate candidate with potential but significant gaps to address."
        else:
            summary = "Candidate may not be the best fit for this position."
        
        return summary


def create_candidate_analysis_graph(mcp_client: MCPClient, vector_db: VectorDatabase, a2a_protocol: AgentToAgentProtocol):
    """Create the LangGraph for candidate analysis."""
    
    analyzer = CandidateAnalyzer(mcp_client, vector_db, a2a_protocol)
    
    # Define the state graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("load_profile", lambda state: analyzer.load_candidate_profile(state))
    workflow.add_node("analyze_skills", lambda state: analyzer.analyze_skills(state))
    workflow.add_node("analyze_experience", lambda state: analyzer.analyze_experience(state))
    workflow.add_node("analyze_portfolio", lambda state: analyzer.analyze_portfolio(state))
    workflow.add_node("assess_cultural_fit", lambda state: analyzer.assess_cultural_fit(state))
    workflow.add_node("generate_assessment", lambda state: analyzer.generate_final_assessment(state))
    
    # Define edges
    workflow.set_entry_point("load_profile")
    workflow.add_edge("load_profile", "analyze_skills")
    workflow.add_edge("analyze_skills", "analyze_experience")
    workflow.add_edge("analyze_experience", "analyze_portfolio")
    workflow.add_edge("analyze_portfolio", "assess_cultural_fit")
    workflow.add_edge("assess_cultural_fit", "generate_assessment")
    workflow.add_edge("generate_assessment", END)
    
    return workflow.compile()


async def run_candidate_analysis(candidate_id: str, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Run the candidate analysis workflow."""
    
    # Initialize components
    mcp_client = MCPClient()
    vector_db = VectorDatabase()
    a2a_protocol = AgentToAgentProtocol(kafka_client=None, agent_id="candidate_finder_agent")
    
    # Create initial state
    initial_state = AnalysisState(
        candidate_id=candidate_id,
        job_requirements=job_requirements
    )
    
    # Create and run workflow
    graph = create_candidate_analysis_graph(mcp_client, vector_db, a2a_protocol)
    
    try:
        result = await graph.ainvoke(initial_state)
        return {
            "success": True,
            "candidate_id": candidate_id,
            "analysis": result.analysis_results,
            "is_complete": result.is_complete
        }
    except Exception as e:
        logger.error(f"Error in candidate analysis: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        await mcp_client.close()
        vector_db.close() 