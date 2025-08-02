from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    The state of an agent.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    flight_query: Dict[str, Any]
    searcher_results: List[Dict[str, Any]]
    processed_flights: List[Dict[str, Any]]
    current_step: str
    error_message: Optional[str]
    has_error: bool
    user_context: Dict[str, Any]
    api_calls_made: int
    search_metadata: Dict[str, Any]

def create_initial_state(user_message:str) -> AgentState:
    """
    Initialize the agent state with the user message.
    """
    return AgentState(
        message=[],
        flight_query={},
        searcher_results=[],
        processed_flights=[],
        current_step="initial",
        error_message=None,
        has_error=False,
        user_context={},
        api_calls_made=0,
        search_metadata={},
    )
