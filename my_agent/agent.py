import os
from dotenv import load_dotenv
from pathlib import Path

# Load the .env that sits next to agent.py (inside my_agent/)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import VertexAiSearchTool
# ADD THIS
from google.adk.tools.google_search_tool import GoogleSearchTool

# Configuration (Replace with your IDs)
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASTORE_ID = os.getenv("DATASTORE_ID")

# --- AGENT 1: THE RESUME PARSER ---
# Extracts structured data from raw text and saves it to 'parsed_skills'
parser_agent = LlmAgent(
    name="ResumeParser",
    model="gemini-2.5-flash-lite",
    instruction="Extract a comma-separated list of technical skills from this resume: {resume_text}",
    tools=[],
    output_key="parsed_skills"
)

# --- AGENT 2: THE GAP RESEARCHER ---
search_tool = VertexAiSearchTool(data_store_id=DATASTORE_ID)

researcher_agent = LlmAgent(
    name="GapAnalyst",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a Career Gap Analyst. 
    1. Use the VertexAiSearchTool to find the closest match in the job catalog for the user's custom role: '{target_role}'.
    2. If an exact match isn't found, look for roles with similar skill sets.
    3. Extract the 'REQUIRED SKILLS' and 'CERTIFICATIONS'.
    4. Compare these against the user's skills: '{parsed_skills}'.
    5. List only the skills and certifications the user is missing.
    """,
    tools=[search_tool],
    output_key="skill_gaps"
)

# --- AGENT 3: THE STRATEGIST ---
# Builds a supportive 4-week roadmap based on researched gaps
google_search_tool = GoogleSearchTool()
strategist_agent = LlmAgent(
    name="CareerCoach",
    model="gemini-2.5-flash-lite",
    instruction="""
    1. Take the {skill_gaps} identified.
    2. Use Google Search to find the top-rated certification, at least 3 high-quality courses (Coursera/Udemy/EDX/Youtube) and relevant articles for each gap.
    3. Create a 8-week roadmap with day-wise planning and actionable insights.
    4. Include these specific URLs of everything that is recommended.
    5. The URLS must be clickable so that the user is directed to the specific course upon clicking the link.
    6. Use an encouraging tone.
    """,
    tools=[google_search_tool],
    output_key="career_roadmap"
)

# --- AGENT 4: THE INTERVIEW COACH ---
# Generates realistic questions to test the user's new roadmap
interview_agent = LlmAgent(
    name="InterviewCoach",
    model="gemini-2.5-flash-lite",
    instruction="""Based on the roadmap: {career_roadmap}, generate 3 challenging interview questions. 
    Explain why these questions are important for a {target_role} role.""",
    tools=[],
    output_key="interview_questions"
)

# Create the team
career_team = SequentialAgent(
    name="SkillBridge_Navigator",
    sub_agents=[parser_agent, researcher_agent, strategist_agent, interview_agent]
)

