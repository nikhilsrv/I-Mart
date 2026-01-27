"""
LangGraph agent for I-Mart voice assistant.
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.config import settings
from src.prompts import SYSTEM_PROMPT
from src.tools import ALL_TOOLS


def create_agent():
    """Create and return the LangGraph agent."""

    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.7,
        max_tokens=256,  # Keep responses concise for voice
    )

    # Create memory for conversation persistence
    memory = MemorySaver()

    # Create the ReAct agent with tools
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        checkpointer=memory,
        state_modifier=SYSTEM_PROMPT,
    )

    return agent


# Singleton agent instance
_agent = None


def get_agent():
    """Get or create the agent instance."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


async def process_message(message: str, session_id: str) -> str:
    """
    Process a user message and return the agent's response.

    Args:
        message: User's text input (from STT)
        session_id: Unique session identifier for conversation memory

    Returns:
        Agent's text response (to be sent to TTS)
    """
    agent = get_agent()

    config = {"configurable": {"thread_id": session_id}}

    result = await agent.ainvoke(
        {"messages": [("user", message)]},
        config=config,
    )

    # Extract the last AI message
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if ai_messages:
        return ai_messages[-1].content

    return "I'm sorry, I didn't understand that. Could you please repeat?"
