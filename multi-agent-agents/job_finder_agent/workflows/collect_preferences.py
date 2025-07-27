"""
Job Finder Agent - Collect Preferences Workflow

This workflow collects candidate preferences and builds their profile
for job matching.
"""

import logging
from typing import Dict, Any, List
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from common.mcp_client import MCPClient, ToolType
from common.vector_db import VectorDatabase

logger = logging.getLogger(__name__)


class CandidateState(BaseModel):
    """State for candidate preference collection."""
    
    candidate_id: str
    conversation_history: List[Dict[str, str]] = []
    collected_data: Dict[str, Any] = {}
    current_step: str = "initial_greeting"
    is_complete: bool = False
    error_message: str = ""
    
    # Preference fields
    name: str = ""
    email: str = ""
    skills: List[str] = []
    experience_years: int = 0
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    salary_expectation: str = ""
    remote_preference: bool = False
    work_experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    portfolio_links: List[str] = []
    resume_url: str = ""


class PreferenceCollector:
    """Collects candidate preferences through conversation."""
    
    def __init__(self, mcp_client: MCPClient, vector_db: VectorDatabase):
        self.mcp_client = mcp_client
        self.vector_db = vector_db
        self.conversation_steps = [
            "initial_greeting",
            "collect_basic_info",
            "collect_skills",
            "collect_experience",
            "collect_preferences",
            "collect_portfolio",
            "finalize_profile"
        ]
    
    def get_next_question(self, state: CandidateState) -> str:
        """Get the next question based on current step."""
        if state.current_step == "initial_greeting":
            return "Hello! I'm your Job Finder Agent. I'll help you find the perfect job match. Let's start by getting to know you better. What's your name?"
        
        elif state.current_step == "collect_basic_info":
            if not state.name:
                return "What's your name?"
            elif not state.email:
                return f"Nice to meet you, {state.name}! What's your email address?"
        
        elif state.current_step == "collect_skills":
            return "Great! Now let's talk about your skills. What are your main technical skills? (e.g., Python, JavaScript, React, etc.)"
        
        elif state.current_step == "collect_experience":
            if not state.skills:
                return "Let's talk about your experience. How many years of professional experience do you have?"
            else:
                return f"Thanks! I see you have skills in {', '.join(state.skills[:3])}. How many years of professional experience do you have?"
        
        elif state.current_step == "collect_preferences":
            if not state.experience_years:
                return "What types of roles are you looking for? (e.g., Software Engineer, Data Scientist, Product Manager)"
            else:
                return f"Perfect! With {state.experience_years} years of experience, what types of roles are you looking for?"
        
        elif state.current_step == "collect_portfolio":
            return "Do you have any portfolio links, GitHub profile, or other work samples you'd like to share?"
        
        elif state.current_step == "finalize_profile":
            return "Excellent! I have all the information I need. Let me create your profile and start looking for matching jobs. Is there anything else you'd like to add or modify?"
        
        return "Thank you for the information! Let me process this and find you the best job matches."
    
    def process_answer(self, state: CandidateState, answer: str) -> CandidateState:
        """Process the candidate's answer and update state."""
        try:
            if state.current_step == "initial_greeting":
                state.name = answer.strip()
                state.current_step = "collect_basic_info"
                state.collected_data["name"] = state.name
            
            elif state.current_step == "collect_basic_info":
                if not state.name:
                    state.name = answer.strip()
                    state.collected_data["name"] = state.name
                    return self.process_answer(state, "")
                elif not state.email:
                    state.email = answer.strip()
                    state.collected_data["email"] = state.email
                    state.current_step = "collect_skills"
            
            elif state.current_step == "collect_skills":
                # Parse skills from answer
                skills = [skill.strip() for skill in answer.split(',') if skill.strip()]
                state.skills = skills
                state.collected_data["skills"] = skills
                state.current_step = "collect_experience"
            
            elif state.current_step == "collect_experience":
                # Try to extract years from answer
                import re
                years_match = re.search(r'(\d+)', answer)
                if years_match:
                    state.experience_years = int(years_match.group(1))
                else:
                    state.experience_years = 0
                state.collected_data["experience_years"] = state.experience_years
                state.current_step = "collect_preferences"
            
            elif state.current_step == "collect_preferences":
                # Parse preferred roles
                roles = [role.strip() for role in answer.split(',') if role.strip()]
                state.preferred_roles = roles
                state.collected_data["preferred_roles"] = roles
                state.current_step = "collect_portfolio"
            
            elif state.current_step == "collect_portfolio":
                # Parse portfolio links
                links = [link.strip() for link in answer.split(',') if link.strip()]
                state.portfolio_links = links
                state.collected_data["portfolio_links"] = links
                state.current_step = "finalize_profile"
            
            elif state.current_step == "finalize_profile":
                state.is_complete = True
            
            # Add to conversation history
            state.conversation_history.append({
                "role": "user",
                "content": answer
            })
            
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            state.error_message = str(e)
        
        return state
    
    async def analyze_portfolio(self, state: CandidateState) -> CandidateState:
        """Analyze portfolio links using MCP tools."""
        if not state.portfolio_links:
            return state
        
        for link in state.portfolio_links:
            if "github.com" in link:
                # Extract username from GitHub URL
                username = link.split("github.com/")[-1].split("/")[0]
                response = await self.mcp_client.analyze_github_profile(username)
                if response.success:
                    state.collected_data["github_analysis"] = response.result
            
            elif "linkedin.com" in link:
                # LinkedIn analysis would go here
                state.collected_data["linkedin_analysis"] = {"status": "analyzed"}
        
        return state
    
    async def store_in_vector_db(self, state: CandidateState) -> CandidateState:
        """Store candidate profile in vector database."""
        try:
            # Create embedding for candidate profile
            profile_text = f"""
            Name: {state.name}
            Skills: {', '.join(state.skills)}
            Experience: {state.experience_years} years
            Preferred Roles: {', '.join(state.preferred_roles)}
            Portfolio: {', '.join(state.portfolio_links)}
            """
            
            # Store in vector database
            await self.vector_db.add_document(
                collection_name="candidates",
                document_id=state.candidate_id,
                text=profile_text,
                metadata=state.collected_data
            )
            
            logger.info(f"Stored candidate profile for {state.candidate_id}")
            
        except Exception as e:
            logger.error(f"Error storing in vector DB: {e}")
            state.error_message = str(e)
        
        return state


def create_preference_collection_graph(mcp_client: MCPClient, vector_db: VectorDatabase):
    """Create the LangGraph for preference collection."""
    
    collector = PreferenceCollector(mcp_client, vector_db)
    
    # Define the state graph
    workflow = StateGraph(CandidateState)
    
    # Add nodes
    workflow.add_node("get_question", lambda state: {"question": collector.get_next_question(state)})
    workflow.add_node("process_answer", lambda state, answer: collector.process_answer(state, answer))
    workflow.add_node("analyze_portfolio", lambda state: collector.analyze_portfolio(state))
    workflow.add_node("store_profile", lambda state: collector.store_in_vector_db(state))
    
    # Define edges
    workflow.set_entry_point("get_question")
    
    workflow.add_edge("get_question", "process_answer")
    workflow.add_edge("process_answer", "analyze_portfolio")
    workflow.add_edge("analyze_portfolio", "store_profile")
    workflow.add_edge("store_profile", END)
    
    return workflow.compile()


async def run_preference_collection(candidate_id: str, initial_message: str = None) -> Dict[str, Any]:
    """Run the preference collection workflow."""
    
    # Initialize components
    mcp_client = MCPClient()
    vector_db = VectorDatabase()
    
    # Create initial state
    initial_state = CandidateState(
        candidate_id=candidate_id,
        conversation_history=[]
    )
    
    if initial_message:
        initial_state.conversation_history.append({
            "role": "user",
            "content": initial_message
        })
    
    # Create and run workflow
    graph = create_preference_collection_graph(mcp_client, vector_db)
    
    try:
        result = await graph.ainvoke(initial_state)
        return {
            "success": True,
            "state": result,
            "profile_complete": result.is_complete
        }
    except Exception as e:
        logger.error(f"Error in preference collection: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        await mcp_client.close()
        vector_db.close() 