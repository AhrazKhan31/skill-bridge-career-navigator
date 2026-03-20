import streamlit as st
import os
import asyncio
import re
from pathlib import Path
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load root .env 
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Fix Windows credential path encoding issues
adc_path = Path.home() / "AppData" / "Roaming" / "gcloud" / "application_default_credentials.json"
if adc_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(adc_path)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from my_agent.agent import career_team

st.set_page_config(page_title="SkillBridge Career Navigator", layout="wide")

# RULE-BASED FALLBACK 
# Used when AI is unavailable or returns empty
COMMON_SKILL_KEYWORDS = [
    "python", "java", "sql", "aws", "azure", "gcp", "docker", "kubernetes",
    "react", "node", "javascript", "typescript", "ml", "ai", "tensorflow",
    "pytorch", "spark", "hadoop", "tableau", "power bi", "excel", "git",
    "linux", "terraform", "ansible", "ci/cd", "rest api", "mongodb", "postgresql"
]

def fallback_extract_skills(resume_text: str) -> str:
    """Rule-based skill extractor when AI is unavailable."""
    text_lower = resume_text.lower()
    found = [skill for skill in COMMON_SKILL_KEYWORDS if skill in text_lower]
    if found:
        return ", ".join(found)
    return "No recognizable skills found (manual review needed)"

def fallback_roadmap(skill_gaps: str) -> str:
    """Rule-based roadmap when AI is unavailable."""
    gaps = [g.strip() for g in skill_gaps.split(",") if g.strip()]
    if not gaps:
        return "No skill gaps identified. Review your resume manually."
    roadmap = "**4-Week Manual Roadmap (AI unavailable)**\n\n"
    for i, gap in enumerate(gaps[:4], 1):
        roadmap += f"**Week {i}:** Focus on `{gap}` — search Coursera or YouTube for beginner courses.\n\n"
    return roadmap


# INPUT VALIDATION 
def validate_inputs(uploaded_file, role_choice: str) -> list[str]:
    errors = []
    if uploaded_file is None:
        errors.append("Please upload a PDF resume.")
    if not role_choice or not role_choice.strip():
        errors.append("Please enter a target role.")
    elif len(role_choice.strip()) < 3:
        errors.append("Target role must be at least 3 characters.")
    elif not re.search(r'[a-zA-Z]', role_choice):
        errors.append("Target role must contain letters.")
    return errors

def parse_resume(uploaded_file) -> tuple[str, list[str]]:
    """Returns (text, errors)."""
    try:
        reader = PdfReader(uploaded_file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        if len(text.strip()) < 50:
            return text, ["Resume appears too short or could not be read. Please check your PDF."]
        return text, []
    except Exception as e:
        return "", [f"Failed to read PDF: {str(e)}"]


# AI RUNNER
async def run_career_team(resume_text: str, target_role: str) -> dict:
    session_service = InMemorySessionService()
    initial_state = {"resume_text": resume_text, "target_role": target_role}
    session = await session_service.create_session(
        app_name="skillbridge", user_id="streamlit_user", state=initial_state
    )
    runner = Runner(agent=career_team, app_name="skillbridge", session_service=session_service)
    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"Analyze resume for role: {target_role}")]
    )
    async for event in runner.run_async(
        user_id="streamlit_user", session_id=session.id, new_message=message
    ):
        pass
    final_session = await session_service.get_session(
        app_name="skillbridge", user_id="streamlit_user", session_id=session.id
    )
    return final_session.state

# UI
st.title("🚀 SkillBridge Career Navigator")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
role_choice = st.text_input(
    "What is your Target Role?",
    placeholder="e.g. Senior Cloud Architect, Junior Data Analyst..."
)

# GENERATE BUTTON
if st.button("Generate My Roadmap", type="primary"):
    errors = validate_inputs(uploaded_file, role_choice)
    if errors:
        for e in errors:
            st.error(e)
    else:
        resume_text, parse_errors = parse_resume(uploaded_file)
        if parse_errors:
            for e in parse_errors:
                st.error(e)
        else:
            # Store inputs in session state to enable Update flow
            st.session_state["resume_text"] = resume_text
            st.session_state["role_choice"] = role_choice
            st.session_state["result"] = None  # clear old result

            with st.spinner("Agents are collaborating... this may take 30–60 seconds"):
                try:
                    result = asyncio.run(run_career_team(resume_text, role_choice))
                    # AI Fallback: if AI returns empty outputs, use rule-based
                    if not result.get("parsed_skills"):
                        st.warning("⚠️ AI skill extraction failed. Using rule-based fallback.")
                        result["parsed_skills"] = fallback_extract_skills(resume_text)
                    if not result.get("career_roadmap"):
                        st.warning("⚠️ AI roadmap generation failed. Using rule-based fallback.")
                        result["career_roadmap"] = fallback_roadmap(result.get("skill_gaps", ""))
                    st.session_state["result"] = result
                except Exception as e:
                    st.warning(f"⚠️ AI unavailable ({type(e).__name__}). Showing rule-based results.")
                    parsed = fallback_extract_skills(resume_text)
                    st.session_state["result"] = {
                        "parsed_skills": parsed,
                        "skill_gaps": "Could not determine gaps (AI offline)",
                        "career_roadmap": fallback_roadmap(parsed),
                        "interview_questions": "AI offline — search common interview questions for your role on Glassdoor."
                    }

# DISPLAY RESULTS
if st.session_state.get("result"):
    result = st.session_state["result"]
    st.success("✅ Analysis Complete!")

    # SEARCH/FILTER 
    st.subheader("🔍 Filter Results")
    search_term = st.text_input("Search within results", placeholder="e.g. Python, Week 2, certification...")

    def highlight_html(text: str, term: str) -> str:
        """Wraps matched terms in a bright yellow highlighted span."""
        if not term:
            return text
        escaped = re.escape(term)
        return re.sub(
            f"({escaped})",
            r'<mark style="background-color: #FFD700; color: #000000; '
            r'padding: 2px 4px; border-radius: 3px; font-weight: bold;">\1</mark>',
            text,
            flags=re.IGNORECASE
        )

    def render(text: str, term: str, use_markdown: bool = False):
        """Renders text with or without highlight, plus a match counter."""
        if term:
            matches = len(re.findall(re.escape(term), text, re.IGNORECASE))
            if matches:
                st.caption(f"🟡 {matches} match{'es' if matches > 1 else ''} found for '{term}'")
            else:
                st.caption(f"❌ No matches for '{term}'")
            st.markdown(highlight_html(text, term), unsafe_allow_html=True)
        else:
            if use_markdown:
                st.markdown(text)
            else:
                st.write(text)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Extracted Skills")
        skills_text = result.get("parsed_skills", "None found")
        render(skills_text, search_term)

        st.subheader("❌ Skill Gaps")
        gaps_text = result.get("skill_gaps", "None identified")
        render(gaps_text, search_term)

    with col2:
        st.subheader("🗺️ Your Roadmap")
        roadmap_text = result.get("career_roadmap", "No roadmap generated.")
        render(roadmap_text, search_term, use_markdown=True)

        st.subheader("🎤 Interview Questions")
        st.info(result.get("interview_questions", "No questions generated."))

    # UPDATE FLOW
    st.divider()
    st.subheader("🔄 Refine Your Analysis")
    new_role = st.text_input(
        "Change target role and re-run:",
        value=st.session_state.get("role_choice", ""),
        key="update_role"
    )
    if st.button("Update Analysis"):
        update_errors = validate_inputs(uploaded_file, new_role)
        if update_errors:
            for e in update_errors:
                st.error(e)
        else:
            with st.spinner("Re-running with updated role..."):
                try:
                    updated_result = asyncio.run(
                        run_career_team(st.session_state["resume_text"], new_role)
                    )
                    if not updated_result.get("career_roadmap"):
                        updated_result["career_roadmap"] = fallback_roadmap(
                            updated_result.get("skill_gaps", "")
                        )
                    st.session_state["result"] = updated_result
                    st.session_state["role_choice"] = new_role
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {type(e).__name__}. Please try again.")