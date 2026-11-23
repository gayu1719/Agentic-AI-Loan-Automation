"""Base agent class for all LOS agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
import structlog

logger = structlog.get_logger()


class AgentInput(BaseModel):
    """Base input model for agents."""
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentOutput(BaseModel):
    """Base output model for agents."""
    result: Dict[str, Any]
    metadata: Dict[str, Any]
    confidence_score: float
    recommendations: Optional[List[str]] = None


class BaseAgent(ABC):
    """Base class for all LOS agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[Tool]] = None,
        langfuse_handler: Optional[CallbackHandler] = None
    ):
        self.name = name
        self.description = description
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1
        )
        self.tools = tools or []
        self.langfuse_handler = langfuse_handler
        self.logger = logger.bind(agent=name)
        
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the input data and return the result."""
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Get the prompt template for this agent."""
        pass
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate the input data."""
        return True
    
    def validate_output(self, output: AgentOutput) -> bool:
        """Validate the output data."""
        return output.confidence_score >= 0.0
    
    async def _log_execution(self, input_data: AgentInput, output: AgentOutput):
        """Log agent execution for monitoring."""
        self.logger.info(
            "Agent executed",
            input_size=len(str(input_data.data)),
            output_confidence=output.confidence_score,
            recommendations_count=len(output.recommendations or [])
        ) 