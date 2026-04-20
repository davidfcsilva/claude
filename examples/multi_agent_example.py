"""
Multi-Agent Example - Research Team with LangChain

This example demonstrates:
- Multiple specialized agents working together
- Task delegation between agents
- Sequential workflow with memory

This simulates a research team with:
- Researcher: Searches for information
- Analyst: Analyzes and summarizes findings
- Writer: Drafts reports based on analysis
"""

from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from typing import List

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

class ResearchAgent:
    """Research agent - searches for information"""

    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="agent_scratchpad"
        )
        self.tools = self._get_research_tools()

        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )

    def _get_research_tools(self):
        return [
            Tool(
                name="WebSearch",
                func=self._search,
                description="Search for information on the web"
            ),
            Tool(
                name="KnowledgeBase",
                func=self._knowledge_base,
                description="Search internal knowledge base"
            ),
        ]

    def _search(self, query: str) -> str:
        """Mock search function"""
        return f"Search results for '{query}': Found relevant information..."

    def _knowledge_base(self, topic: str) -> str:
        """Mock knowledge base lookup"""
        return f"Knowledge base entry for '{topic}': Contains relevant data..."

    def search(self, query: str) -> str:
        """Perform research search"""
        return self.agent.run(query)


class AnalystAgent:
    """Analyst agent - analyzes and summarizes information"""

    def __init__(self, llm):
        self.llm = llm
        self.tools = [
            Tool(
                name="Summarize",
                func=self._summarize,
                description="Summarize the provided information"
            ),
            Tool(
                name="Analyze",
                func=self._analyze,
                description="Analyze the given data"
            ),
        ]

        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def _summarize(self, text: str) -> str:
        """Create a summary of provided text"""
        return f"Summary of provided text: {text[:100]}..."

    def _analyze(self, data: str) -> str:
        """Analyze provided data"""
        return f"Analysis of provided data: Shows interesting patterns in: {data[:100]}..."

    def analyze(self, information: str) -> str:
        """Perform analysis on information"""
        return self.agent.run(f"Please analyze: {information}")


class WriterAgent:
    """Writer agent - drafts reports based on analysis"""

    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="agent_scratchpad"
        )

        self.agent = initialize_agent(
            [
                Tool(
                    name="DraftReport",
                    func=self._draft_report,
                    description="Draft a report based on provided information"
                ),
                Tool(
                    name="Review",
                    func=self._review,
                    description="Review and refine a draft"
                ),
            ],
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )

    def _draft_report(self, analysis: str) -> str:
        """Draft a report from analysis"""
        return f"DRAFT REPORT:\n\nBased on analysis:\n{analysis}\n\n--- Report draft created ---"

    def _review(self, draft: str) -> str:
        """Review and refine a draft"""
        return f"REVIEWED DRAFT:\n\n{draft[:150]}...\n\n[Review comments added]"

    def write_report(self, analysis: str) -> str:
        """Write a report based on analysis"""
        return self.agent.run(f"Please write a report based on this analysis:\n{analysis}")


# =============================================================================
# RESEARCH TEAM WORKFLOW
# =============================================================================

class ResearchTeam:
    """
    Orchestrates research workflow with multiple agents.

    Workflow:
    1. Researcher searches for information
    2. Analyst analyzes findings
    3. Writer drafts final report
    """

    def __init__(self, llm):
        self.llm = llm
        self.researcher = ResearchAgent(llm)
        self.analyst = AnalystAgent(llm)
        self.writer = WriterAgent(llm)

    def research_workflow(self, topic: str) -> dict:
        """
        Execute full research workflow.

        Args:
            topic: Research topic to investigate

        Returns:
            Dictionary with workflow results
        """
        print("=" * 60)
        print("RESEARCH WORKFLOW STARTED")
        print("=" * 60)

        # Step 1: Researcher searches
        print(f"\n[Step 1] Researcher is searching for: {topic}")
        research_results = self.researcher.search(f"{topic} research and recent developments")
        print(f"Research results:\n{research_results}\n")

        # Step 2: Analyst analyzes
        print(f"[Step 2] Analyst is analyzing research findings...")
        analysis_results = self.analyst.analyze(research_results)
        print(f"Analysis results:\n{analysis_results}\n")

        # Step 3: Writer drafts report
        print(f"[Step 3] Writer is drafting final report...")
        report = self.writer.write_report(analysis_results)
        print(f"Final report:\n{report}\n")

        return {
            "topic": topic,
            "research": research_results,
            "analysis": analysis_results,
            "report": report,
        }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Initialize team (replace with your API key)
    # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    # team = ResearchTeam(llm)

    print("=" * 60)
    print("Multi-Agent Research Team Example")
    print("LangChain Framework")
    print("=" * 60)
    print("\nThis example demonstrates how to create multiple specialized")
    print("agents that work together in a research team workflow.")
    print("\nTo run with real LLM:")
    print("  1. Set OPENAI_API_KEY environment variable")
    print("  2. Uncomment the initialization code above")
    print("  3. Run: python examples/multi_agent_example.py\n")

    # Show what agents can do
    print("AGENT CAPABILITIES:\n")
    print("┌─────────────┐")
    print("│ RESEARCHER  │")
    print("│ - Web Search")
    print("│ - Knowledge Base")
    print("│ - Information Gathering")
    print("└─────────────┘")
    print()
    print("┌─────────────┐")
    print("│ ANALYST     │")
    print("│ - Analysis")
    print("│ - Summarization")
    print("│ - Data Interpretation")
    print("└─────────────┘")
    print()
    print("┌─────────────┐")
    print("│ WRITER      │")
    print("│ - Report Drafting")
    print("│ - Review & Refine")
    print("│ - Documentation")
    print("└─────────────┘")

    print("\n" + "=" * 60)
    print("END OF EXAMPLE")
    print("=" * 60)
