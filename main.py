import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

AUTHOR=os.getenv('AUTHOR')

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from hepara.agent import hep_coordinator
from hepara.subagents.inspirehep_agent.tools import track_citations_updates

def print_citation_update(update: dict) -> None:
    if "Error" in update:
        print(f"Citation update check failed: {update['Error']}\n")
        return

    result = update.get("Result")
    if isinstance(result, str):
        print(f"Citation update: {result}\n")
        return

    print("Citation updates:")
    for publication in result.get("New Publications", []): # type: ignore
        arxiv_id = publication.get("arXiv ID", "N/A")
        citations = publication.get("Citations", 0)
        print(f"  New publication: {publication.get('Title', 'N/A')} ({arxiv_id}, {citations} citations)")
    for citation in result.get("Citation Updates", []): # type: ignore
        increase = citation.get("Increase", 0)
        current = citation.get("Current", 0)
        print(f"  +{increase} citations: {citation.get('Title', 'N/A')} ({current} total)")
    print()

async def main():
    print("Welcome to HEPARA!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    runner = InMemoryRunner(agent=hep_coordinator, app_name="HEPARA")

    session_id = "session_1"
    user_id = AUTHOR if AUTHOR else "Guest"

    await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)

    print("Checking citation updates...")
    citation_update = await track_citations_updates()
    print_citation_update(citation_update)

    while True:
        try:
            user_input = await asyncio.to_thread(input, f"{user_id}: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        cleaned_input = user_input.strip()
        if not cleaned_input:
            continue
        if cleaned_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        content = Content(role="user", parts=[Part(text=cleaned_input)])

        async for response in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if response.content and response.content.parts and response.author != "user":
                for part in response.content.parts:
                    if part.text:
                        print(f"{response.author}: {part.text}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
