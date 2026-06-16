import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .prompt import ARXIV_TRACKER_PROMPT
from .tools import recommend_by_trends, search_papers, download_pdf, list_papers

GOOGLE_MODEL = os.getenv("GOOGLE_MODEL") 
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

recommend_by_trends_tool = FunctionTool(func=recommend_by_trends)
search_papers_tool = FunctionTool(func=search_papers)
download_pdf_tool = FunctionTool(func=download_pdf)
list_papers_tool = FunctionTool(func=list_papers)

arxiv_agent = Agent(
    model=model,
    name='arxiv_tracker',
    description="An arXiv tracker that can search papers, download PDF files, track the trending papers in the user's research field.",
    instruction=ARXIV_TRACKER_PROMPT,
    tools=[recommend_by_trends_tool, search_papers_tool, download_pdf_tool, list_papers_tool],
    output_key="arxiv_report"
)
