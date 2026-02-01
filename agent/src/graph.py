"""
LangGraph agent for I-Mart voice assistant.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.config import settings
from src.prompts import SYSTEM_PROMPT
from src.tools import ALL_TOOLS


def create_agent():
    """Create and return the LangGraph agent."""

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7,
        max_output_tokens=256,  # Keep responses concise for voice
        convert_system_message_to_human=True,  # Required for gemini models
    )

    # Create memory for conversation persistence
    memory = MemorySaver()

    # Create the ReAct agent with tools
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        checkpointer=memory,
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

    # Get current state to check if this is the first message
    state = await agent.aget_state(config)

    # Add system prompt only for the first message in a thread
    if not state.values.get("messages"):
        result = await agent.ainvoke(
            {"messages": [("system", SYSTEM_PROMPT), ("user", message)]},
            config=config,
        )
    else:
        result = await agent.ainvoke(
            {"messages": [("user", message)]},
            config=config,
        )

    # Extract the last AI message
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if ai_messages:
        content = ai_messages[-1].content

        # Handle both string content and structured content (list of blocks)
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Extract text from content blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    text_parts.append(block)
            return " ".join(text_parts).strip()
        else:
            return str(content)

    return "I'm sorry, I didn't understand that. Could you please repeat?"
