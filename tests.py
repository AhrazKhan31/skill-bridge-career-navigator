import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / "my_agent/.env")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from my_agent.agent import parser_agent

# Import fallback functions directly from app
sys.path.insert(0, str(Path(__file__).parent))
from app import fallback_extract_skills, fallback_roadmap

# ──────────────────────────────────────────────
# Helper to run a single agent
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# TEST 1: HAPPY PATH — AI skill extraction
# ──────────────────────────────────────────────
async def test_happy_path():
    print("=" * 50)
    print("TEST 1: Happy Path — AI Skill Extraction")
    print("=" * 50)
    sample_resume = "Experienced Software Engineer with skills in Python, Docker, and Google Cloud Platform. 5 years experience building REST APIs."

    try:
        result = await run_single_agent(parser_agent, {"resume_text": sample_resume})
        parsed = result.get("parsed_skills", "")
        if parsed and any(skill in parsed for skill in ["Python", "Docker", "Google Cloud"]):
            print(f"✅ PASSED: Skills extracted correctly — {parsed}\n")
        else:
            print(f"❌ FAILED: Unexpected output — '{parsed}'\n")
    except Exception as e:
        print(f"❌ FAILED with exception: {e}\n")


# ──────────────────────────────────────────────
# TEST 2: EDGE CASE — Empty resume input
# ──────────────────────────────────────────────
async def test_edge_case_empty():
    print("=" * 50)
    print("TEST 2: Edge Case — Empty Resume Input")
    print("=" * 50)
    try:
        result = await run_single_agent(parser_agent, {"resume_text": ""})
        parsed = result.get("parsed_skills", "")
        print(f"✅ PASSED: Agent handled empty input gracefully. Output: '{parsed}'\n")
    except Exception as e:
        print(f"❌ FAILED: System crashed on empty input. Error: {e}\n")


# ──────────────────────────────────────────────
# TEST 3: FALLBACK — Skill extraction fallback
# Tests rule-based extractor when AI is unavailable
# ──────────────────────────────────────────────
def test_fallback_skill_extraction():
    print("=" * 50)
    print("TEST 3: Fallback — Rule-Based Skill Extraction")
    print("=" * 50)

    # Case A: Resume with known keywords
    resume_with_skills = "I have experience with Python, Docker, AWS, and PostgreSQL."
    result = fallback_extract_skills(resume_with_skills)
    expected = ["python", "docker", "aws", "postgresql"]
    if all(skill in result.lower() for skill in expected):
        print(f"✅ PASSED (known skills): Extracted — {result}")
    else:
        print(f"❌ FAILED (known skills): Got — '{result}'")

    # Case B: Resume with no recognizable skills
    resume_no_skills = "I enjoy cooking and hiking on weekends."
    result_empty = fallback_extract_skills(resume_no_skills)
    if "No recognizable skills found" in result_empty:
        print(f"✅ PASSED (no skills): Correctly returned — '{result_empty}'")
    else:
        print(f"❌ FAILED (no skills): Got — '{result_empty}'")

    # Case C: Empty string input
    result_blank = fallback_extract_skills("")
    if "No recognizable skills found" in result_blank:
        print(f"✅ PASSED (empty input): Correctly handled empty string\n")
    else:
        print(f"❌ FAILED (empty input): Got — '{result_blank}'\n")


# ──────────────────────────────────────────────
# TEST 4: FALLBACK — Roadmap generation fallback
# Tests rule-based roadmap when AI is unavailable
# ──────────────────────────────────────────────
def test_fallback_roadmap():
    print("=" * 50)
    print("TEST 4: Fallback — Rule-Based Roadmap Generation")
    print("=" * 50)

    # Case A: Normal skill gaps input
    skill_gaps = "Kubernetes, Terraform, AWS"
    result = fallback_roadmap(skill_gaps)
    if "Week 1" in result and "Kubernetes" in result:
        print(f"✅ PASSED (normal gaps): Roadmap generated with weeks and skills")
    else:
        print(f"❌ FAILED (normal gaps): Got — '{result}'")

    # Case B: Empty skill gaps
    result_empty = fallback_roadmap("")
    if "No skill gaps identified" in result_empty:
        print(f"✅ PASSED (empty gaps): Correctly handled empty gaps — '{result_empty}'")
    else:
        print(f"❌ FAILED (empty gaps): Got — '{result_empty}'")

    # Case C: Single skill gap
    result_single = fallback_roadmap("Docker")
    if "Week 1" in result_single and "Docker" in result_single:
        print(f"✅ PASSED (single gap): Roadmap generated for single skill\n")
    else:
        print(f"❌ FAILED (single gap): Got — '{result_single}'\n")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🧪 Running SkillBridge Test Suite\n")

    # Sync tests (no AI call needed)
    test_fallback_skill_extraction()
    test_fallback_roadmap()

    # Async tests (require GCP credentials)
    asyncio.run(test_happy_path())
    asyncio.run(test_edge_case_empty())

    print("=" * 50)
    print("✅ All tests complete.")
    print("=" * 50)