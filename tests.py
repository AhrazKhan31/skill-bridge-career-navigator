import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / "my_agent/.env")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from my_agent.agent import parser_agent

# Helper to run a single agent
async def run_single_agent(agent, state: dict) -> dict:
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app", user_id="test_user", state=state
    )
    runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
    message = genai_types.Content(
        role="user", parts=[genai_types.Part(text="Run the task.")]
    )
    async for _ in runner.run_async(
        user_id="test_user", session_id=session.id, new_message=message
    ):
        pass
    final = await session_service.get_session(
        app_name="test_app", user_id="test_user", session_id=session.id
    )
    return final.state


# TEST 1: HAPPY PATH
async def test_happy_path():
    print("Running Happy Path Test...")
    sample_resume = "Experienced Software Engineer with skills in Python, Docker, and Google Cloud Platform. 5 years experience building REST APIs."

    try:
        result = await run_single_agent(parser_agent, {"resume_text": sample_resume})
        parsed = result.get("parsed_skills", "")
        if parsed and any(skill in parsed for skill in ["Python", "Docker", "Google Cloud"]):
            print(f"✅ Happy Path Passed: Skills extracted — {parsed}")
        else:
            print(f"❌ Happy Path Failed: Unexpected output — {parsed}")
    except Exception as e:
        print(f"❌ Happy Path Failed with exception: {e}")

# TEST 2: EDGE CASE — Empty Resume
async def test_edge_case_empty():
    print("\nRunning Edge Case Test (Empty Resume)...")
    try:
        result = await run_single_agent(parser_agent, {"resume_text": ""})
        parsed = result.get("parsed_skills", "")
        print(f"✅ Edge Case Passed: Agent handled empty input gracefully. Output: '{parsed}'")
    except Exception as e:
        print(f"❌ Edge Case Failed: System crashed on empty input. Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_happy_path())
    asyncio.run(test_edge_case_empty())