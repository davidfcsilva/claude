"""
LangChain Agent Example - Simple Research Assistant

This example demonstrates:
- Tool-based agents (Search, Calculator)
- Zero-shot-react agent pattern
- Memory management
- Running agents locally

Run this file to see the agent in action!
"""

# =============================================================================
# CONFIGURATION
# =============================================================================

from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory

# =============================================================================
# STEP 1: DEFINE TOOLS
# =============================================================================

@tool
def search(query: str) -> str:
    """
    Search the internet for information.

    Args:
        query: The search query to perform

    Returns:
        Search results summary
    """
    # Placeholder - would integrate with DuckDuckGo, SerpAPI, etc.
    return f"Search results for: {query}"


@tool
def calculate(expression: str) -> str:
    """
    Calculate mathematical expressions.

    Args:
        expression: A mathematical expression to evaluate

    Returns:
        The calculated result
    """
    import math
    try:
        # Safe eval with math functions
        allowed = {"__builtins__": {}}
        allowed["math"] = math
        allowed["abs"] = abs
        allowed["sum"] = sum
        allowed["pow"] = pow
        allowed["sqrt"] = math.sqrt
        return str(eval(expression, allowed))
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time() -> str:
    """
    Get the current date and time.

    Returns:
        Current datetime string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%:%S")


# =============================================================================
# STEP 2: CREATE TOOLS LIST
# =============================================================================

tools = [
    Tool.from_function(
        func=search,
        name="Search",
        description="Search the internet for general information."
    ),
    Tool.from_function(
        func=calculate,
        name="Calculator",
        description="Perform mathematical calculations."
    ),
    Tool.from_function(
        func=get_current_time,
        name="CurrentTime",
        description="Get the current date and time."
    ),
]

# =============================================================================
# STEP 3: CONFIGURE CHAIN WITH MEMORY
# =============================================================================

# Initialize LLM (requires API key set in environment)
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",  # or "gpt-4"
)

# Create conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    output_key="agent_scratchpad"
)

# =============================================================================
# STEP 4: CREATE AND RUN AGENT
# =============================================================================

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,  # Show agent's reasoning steps
    handle_parsing_errors=True
)

# =============================================================================
# STEP 5: RUN EXAMPLE QUERIES
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Research Agent Demo")
    print("=" * 60)

    # Example queries
    queries = [
        "What is 15 times 17?",
        "What is the current time?",
        "Search for recent news about AI developments",
        "Calculate 2+3*4-5",
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print('=' * 60)
        result = agent.run(query)
        print(f"\nAgent's response:\n{result}\n")

    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode - Enter 'quit' to exit")
    print("=" * 60)

    while True:
        user_input = input("\nYour query: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input:
            result = agent.run(user_input)
            print(f"\nAgent's response:\n{result}\n")
