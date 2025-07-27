"""
Model Context Protocol (MCP) Client

This module implements the MCP client for agent-to-tool communication,
allowing agents to interact with various tools and services.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import httpx

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Types of tools available through MCP."""
    
    # Portfolio analysis tools
    GITHUB_ANALYSIS = "github_analysis"
    LINKEDIN_ANALYSIS = "linkedin_analysis"
    PORTFOLIO_WEBSITE = "portfolio_website"
    
    # Document analysis tools
    RESUME_PARSER = "resume_parser"
    COVER_LETTER_ANALYZER = "cover_letter_analyzer"
    CERTIFICATE_VERIFIER = "certificate_verifier"
    
    # Communication tools
    EMAIL_SENDER = "email_sender"
    CALENDAR_SCHEDULER = "calendar_scheduler"
    VIDEO_CALL_SCHEDULER = "video_call_scheduler"
    
    # Research tools
    COMPANY_RESEARCHER = "company_researcher"
    SALARY_ANALYZER = "salary_analyzer"
    MARKET_TRENDS = "market_trends"


@dataclass
class ToolRequest:
    """Request structure for tool execution."""
    
    tool_id: str
    tool_type: ToolType
    parameters: Dict[str, Any]
    context: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, urgent
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class ToolResponse:
    """Response structure from tool execution."""
    
    request_id: str
    tool_id: str
    success: bool
    result: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MCPClient:
    """Model Context Protocol client for tool communication."""
    
    def __init__(self, base_url: str = "http://localhost:8080/mcp", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.tool_registry = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        self.register_tool(
            ToolType.GITHUB_ANALYSIS,
            "github_analyzer",
            "Analyze GitHub profile and repositories"
        )
        self.register_tool(
            ToolType.RESUME_PARSER,
            "resume_parser",
            "Parse and extract information from resumes"
        )
        self.register_tool(
            ToolType.EMAIL_SENDER,
            "email_sender",
            "Send emails to candidates or employers"
        )
        self.register_tool(
            ToolType.CALENDAR_SCHEDULER,
            "calendar_scheduler",
            "Schedule interviews and meetings"
        )
    
    def register_tool(self, tool_type: ToolType, tool_id: str, description: str):
        """Register a tool with the MCP client."""
        self.tool_registry[tool_type] = {
            "id": tool_id,
            "description": description,
            "type": tool_type
        }
        logger.info(f"Registered tool: {tool_id} ({tool_type.value})")
    
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """Execute a tool through MCP."""
        start_time = datetime.now()
        
        try:
            # Prepare request payload
            payload = {
                "tool_id": request.tool_id,
                "tool_type": request.tool_type.value,
                "parameters": request.parameters,
                "context": request.context,
                "priority": request.priority
            }
            
            # Send request to MCP server
            response = await self.client.post(
                f"{self.base_url}/execute",
                json=payload
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                request_id=result.get("request_id", f"req_{start_time.timestamp()}"),
                tool_id=request.tool_id,
                success=result.get("success", False),
                result=result.get("result", {}),
                error_message=result.get("error_message"),
                execution_time=execution_time,
                metadata=result.get("metadata", {})
            )
            
        except httpx.HTTPError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"HTTP error executing tool {request.tool_id}: {e}")
            return ToolResponse(
                request_id=f"req_{start_time.timestamp()}",
                tool_id=request.tool_id,
                success=False,
                result={},
                error_message=f"HTTP error: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing tool {request.tool_id}: {e}")
            return ToolResponse(
                request_id=f"req_{start_time.timestamp()}",
                tool_id=request.tool_id,
                success=False,
                result={},
                error_message=f"Tool execution error: {str(e)}",
                execution_time=execution_time
            )
    
    async def analyze_github_profile(self, username: str, context: Dict[str, Any] = None) -> ToolResponse:
        """Analyze a GitHub profile."""
        request = ToolRequest(
            tool_id="github_analyzer",
            tool_type=ToolType.GITHUB_ANALYSIS,
            parameters={"username": username},
            context=context or {}
        )
        return await self.execute_tool(request)
    
    async def parse_resume(self, resume_url: str, context: Dict[str, Any] = None) -> ToolResponse:
        """Parse a resume document."""
        request = ToolRequest(
            tool_id="resume_parser",
            tool_type=ToolType.RESUME_PARSER,
            parameters={"resume_url": resume_url},
            context=context or {}
        )
        return await self.execute_tool(request)
    
    async def send_email(self, to_email: str, subject: str, body: str, context: Dict[str, Any] = None) -> ToolResponse:
        """Send an email."""
        request = ToolRequest(
            tool_id="email_sender",
            tool_type=ToolType.EMAIL_SENDER,
            parameters={
                "to_email": to_email,
                "subject": subject,
                "body": body
            },
            context=context or {}
        )
        return await self.execute_tool(request)
    
    async def schedule_interview(self, candidate_email: str, employer_email: str, 
                                interview_date: str, duration_minutes: int = 60,
                                context: Dict[str, Any] = None) -> ToolResponse:
        """Schedule an interview."""
        request = ToolRequest(
            tool_id="calendar_scheduler",
            tool_type=ToolType.CALENDAR_SCHEDULER,
            parameters={
                "candidate_email": candidate_email,
                "employer_email": employer_email,
                "interview_date": interview_date,
                "duration_minutes": duration_minutes,
                "type": "interview"
            },
            context=context or {}
        )
        return await self.execute_tool(request)
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json().get("tools", [])
        except Exception as e:
            logger.error(f"Error getting available tools: {e}")
            return list(self.tool_registry.values())
    
    async def close(self):
        """Close the MCP client."""
        await self.client.aclose()
        logger.info("MCP client closed") 