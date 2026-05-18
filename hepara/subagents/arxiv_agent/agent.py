from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .prompt import ARXIV_TRACKER_PROMPT
from .tools import recommend_by_trends, search_papers, download_pdf

recommend_by_trends_tool = FunctionTool(func=recommend_by_trends)
search_papers_tool = FunctionTool(func=search_papers)
download_pdf_tool = FunctionTool(func=download_pdf)

arxiv_agent = Agent(
    model='gemini-2.5-flash',
    name='arxiv_tracker',
    description="An arXiv tracker that can search papers, download PDF files, track the trending papers in the user's research field.",
    instruction=ARXIV_TRACKER_PROMPT,
    tools=[recommend_by_trends_tool, search_papers_tool, download_pdf_tool],
    output_key="arxiv_report"
)
