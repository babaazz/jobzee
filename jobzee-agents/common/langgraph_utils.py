import logging
from typing import Dict, Any, List, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

class AgentWorkflowBuilder:
    """Builder for creating agent workflows using LangGraph"""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.graph = StateGraph(workflow_name)
        self.nodes = {}
        self.checkpointer = MemorySaver()
        
    def add_node(self, name: str, handler: Callable) -> 'AgentWorkflowBuilder':
        """Add a node to the workflow"""
        self.nodes[name] = handler
        self.graph.add_node(name, handler)
        return self
        
    def add_edge(self, from_node: str, to_node: str, condition: Callable = None) -> 'AgentWorkflowBuilder':
        """Add an edge between nodes"""
        if condition:
            self.graph.add_edge(from_node, to_node, condition)
        else:
            self.graph.add_edge(from_node, to_node)
        return self
        
    def add_conditional_edge(self, from_node: str, condition_map: Dict[str, str]) -> 'AgentWorkflowBuilder':
        """Add conditional edges from a node"""
        self.graph.add_conditional_edges(from_node, condition_map)
        return self
        
    def set_entry_point(self, node_name: str) -> 'AgentWorkflowBuilder':
        """Set the entry point of the workflow"""
        self.graph.set_entry_point(node_name)
        return self
        
    def set_finish_point(self, node_name: str) -> 'AgentWorkflowBuilder':
        """Set the finish point of the workflow"""
        self.graph.add_edge(node_name, END)
        return self
        
    def build(self):
        """Build the workflow graph"""
        return self.graph.compile(checkpointer=self.checkpointer)
        
class WorkflowState:
    """State management for agent workflows"""
    
    def __init__(self, initial_data: Dict[str, Any] = None):
        self.data = initial_data or {}
        self.metadata = {
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp(),
            'steps_completed': [],
            'errors': []
        }
        
    def update(self, key: str, value: Any):
        """Update a value in the state"""
        self.data[key] = value
        self.metadata['updated_at'] = self._get_current_timestamp()
        
    def get(self, key: str, default: Any = None):
        """Get a value from the state"""
        return self.data.get(key, default)
        
    def add_step(self, step_name: str, result: Any = None):
        """Add a completed step to the workflow"""
        self.metadata['steps_completed'].append({
            'step': step_name,
            'result': result,
            'timestamp': self._get_current_timestamp()
        })
        
    def add_error(self, step_name: str, error: str):
        """Add an error to the workflow state"""
        self.metadata['errors'].append({
            'step': step_name,
            'error': error,
            'timestamp': self._get_current_timestamp()
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'data': self.data,
            'metadata': self.metadata
        }
        
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
        
class WorkflowExecutor:
    """Executor for running agent workflows"""
    
    def __init__(self, workflow, config: Dict[str, Any] = None):
        self.workflow = workflow
        self.config = config or {}
        
    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with initial state"""
        try:
            # Create workflow state
            state = WorkflowState(initial_state)
            
            # Execute workflow
            result = await self.workflow.ainvoke(state.to_dict())
            
            # Update state with result
            state.data.update(result)
            
            logger.info(f"Workflow executed successfully. Steps completed: {len(state.metadata['steps_completed'])}")
            return state.to_dict()
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            state = WorkflowState(initial_state)
            state.add_error('workflow_execution', str(e))
            return state.to_dict()
            
    def execute_sync(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow synchronously"""
        try:
            # Create workflow state
            state = WorkflowState(initial_state)
            
            # Execute workflow
            result = self.workflow.invoke(state.to_dict())
            
            # Update state with result
            state.data.update(result)
            
            logger.info(f"Workflow executed successfully. Steps completed: {len(state.metadata['steps_completed'])}")
            return state.to_dict()
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            state = WorkflowState(initial_state)
            state.add_error('workflow_execution', str(e))
            return state.to_dict()
            
class WorkflowMonitor:
    """Monitor for tracking workflow execution"""
    
    def __init__(self):
        self.executions = []
        
    def add_execution(self, execution_id: str, workflow_name: str, 
                     initial_state: Dict[str, Any], result: Dict[str, Any]):
        """Add an execution record"""
        execution = {
            'execution_id': execution_id,
            'workflow_name': workflow_name,
            'initial_state': initial_state,
            'result': result,
            'timestamp': self._get_current_timestamp(),
            'success': len(result.get('metadata', {}).get('errors', [])) == 0
        }
        self.executions.append(execution)
        
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.executions:
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0.0
            }
            
        total = len(self.executions)
        successful = len([e for e in self.executions if e['success']])
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        return {
            'total_executions': total,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': round(success_rate, 2)
        }
        
    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent executions"""
        return sorted(self.executions, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() 