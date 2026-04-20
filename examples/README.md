# LangChain Agent Examples

This directory contains examples of building AI agents with LangChain.

## Prerequisites

```bash
pip install langchain langchain-community langchain-openai python-dotenv
```

### Setup

1. Create a `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
```

## Examples

### 1. Simple Research Agent (`langchain_agent_example.py`)

A basic agent that can:
- Search the web
- Calculate expressions
- Track conversation history

**Run it:**
```bash
# Interactive mode:
python examples/langchain_agent_example.py

# Or run specific queries:
python examples/langchain_agent_example.py <<< "What's the capital of France?"
```

### 2. Multi-Agent Team (`multi_agent_example.py`)

Simulates a research team with:
- **Researcher**: Gathers information
- **Analyst**: Analyzes findings
- **Writer**: Drafts reports

**Run it:**
```bash
python examples/multi_agent_example.py
```

## Key Concepts

### Tools
Functions that the agent can call:
```python
@tool
def my_tool(arg1, arg2):
    """Tool description"""
    return result
```

### Memory
Conversation history using `ConversationBufferMemory`

### Agent Types
- `zero-shot-react-description` - Default, flexible
- `react-json` - Structured output
- `chat-conversational-react-description` - Chained conversations

## Next Steps

- See [`../README.md`](../README.md) for the project overview
- Explore LangChain docs: https://python.langchain.com/docs/
