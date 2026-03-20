# 🚀 SkillBridge Career Navigator

> An AI-powered multi-agent career coaching app that analyzes your resume, identifies skill gaps, and generates a personalized 8-week learning roadmap with curated course links and interview preparation.

---

## 📋 Submission Details

**Candidate Name:** Ahraz Khan

**Scenario Chosen:** Career Skill Gap Analyzer — a tool that parses a user's resume, identifies missing skills for a target role, and generates a personalized learning roadmap using a multi-agent AI pipeline.

**Estimated Time Spent:** 6 hours

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud SDK installed and authenticated
- GCP project with these APIs enabled:
  - Vertex AI API
  - Discovery Engine API
  - Cloud Run API

### Run Commands

```bash
# 1. Clone the repo
git clone https://github.com/AhrazKhan31/skill-bridge-career-navigator.git
cd skill-bridge-career-navigator

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Fill in GCP_PROJECT_ID and DATASTORE_ID in .env
# Do the same for my_agent/.env

# 5. Authenticate with GCP
gcloud auth application-default login

# 6. Run the app
streamlit run app.py
```

### Test Commands

```bash
python tests.py
```

---

## 🤖 AI Disclosure

**Did you use an AI assistant (Copilot, ChatGPT, etc.)?** Yes, Copilot, Claude and Gemini

**How did you verify the suggestions?**
Every code suggestion was tested by actually running the app locally and observing real outputs. For example, the Google ADK runner pattern (using `InMemorySessionService` + `Runner` + `run_async`) was verified by checking whether session state was correctly populated after each agent ran. Import errors, credential errors, and rate limit errors were all caught during live testing and fixed iteratively. Documentation was cross-referenced with the official Google ADK GitHub repo.

**Give one example of a suggestion you rejected or changed:**
The AI initially suggested using `parser_agent.call()` to run a single agent in tests — this method does not exist in Google ADK. I rejected this and replaced it with the correct pattern using `Runner` and `InMemorySessionService`, which is the proper way to execute agents in the ADK framework. The corrected approach was then verified by successfully running the tests end-to-end.

---

## ⚖️ Tradeoffs & Prioritization

**What did you cut to stay within the time limit?**

- **User authentication** — no login/signup; all sessions are anonymous and stateless. Adding Firebase Auth would require significant extra setup time.
- **Persistent history** — results are not saved between sessions. A database (Firestore or PostgreSQL) would be needed for this.
- **PDF export** — users cannot download their roadmap as a formatted PDF. This would require a library like ReportLab and additional UI work.
- **Progress tracker** — no way to mark roadmap items as complete. This would need a backend with per-user state.

**What would you build next if you had more time?**

- User accounts with saved history using Firebase Auth
- LinkedIn URL parsing as an alternative to PDF upload
- Roadmap progress tracker where users can check off completed courses
- Live job board integration pulling real postings from LinkedIn or Indeed APIs
- PDF export of the generated roadmap for offline use
- Email delivery of the roadmap via SendGrid

**Known Limitations:**

- Free tier Vertex AI quota causes rate limit errors (HTTP 429) under heavy or rapid consecutive use
- Scanned or image-based PDFs do not parse correctly since PyPDF2 only extracts embedded text
- Google Search tool may return URLs that are occasionally outdated or paywalled
- The job catalog in Vertex AI Search is limited to pre-loaded roles; very niche roles rely on fuzzy similarity matching
- `asyncio.run()` inside Streamlit can conflict with existing event loops in some environments

---

## 🔗 Live Demo

**[https://skillbridge-app-537062195130.us-central1.run.app](https://skillbridge-app-537062195130.us-central1.run.app)**

---

## 📌 What It Does

1. **Upload your resume** (PDF)
2. **Enter your target role** (any role — free text)
3. The AI pipeline runs 4 agents in sequence:
   - 🔍 Extracts your current skills
   - 📊 Identifies your skill gaps vs the target role
   - 🗺️ Builds an 8-week roadmap with real course URLs
   - 🎤 Generates 3 challenging interview questions
4. **Search and filter** results, or **update your target role** and re-run

---

## 🛠️ Tech Stack

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Frontend         | Streamlit                           |
| Agent Framework  | Google ADK (Agent Development Kit)  |
| LLM              | Gemini 2.5 Flash Lite via Vertex AI |
| Job Search       | Vertex AI Search (Discovery Engine) |
| Web Search       | Google Search Tool                  |
| PDF Parsing      | PyPDF2                              |
| Deployment       | Google Cloud Run                    |
| Containerization | Docker                              |

---

## 📁 Project Structure

```
skill-bridge-career-navigator/
├── app.py                           # Streamlit frontend + AI runner
├── Dockerfile                       # Container configuration
├── requirements.txt                 # Python dependencies
├── tests.py                         # Happy path + edge case tests
├── README.md                        # Project documentation
├── DESIGN.md                        # Architecture and design decisions
├── .env.example                     # Environment variable template
├── .dockerignore                    # Docker build exclusions
├── .gitignore                       # Git exclusions
├── data/
│   ├── synthetic_jobs.csv           # Synthetic jobs dataset
│   ├── synthetic_jobs.jsonl         # Synthetic jobs dataset (JSONL format)
│   └── job_catalog_unstructured.txt # Unstructured job catalog data
└── my_agent/
    ├── __init__.py
    ├── agent.py                     # 4-agent pipeline definition
    └── .env.example                 # Agent env variable template
```

---

## 🧪 Running Tests

```bash
python tests.py
```

Tests cover:

- **Happy Path** — Standard resume with clear skills extracts correctly
- **Edge Case** — Empty resume handled gracefully without crash

---

## 🚀 Deployment (Google Cloud Run)

```bash
gcloud run deploy skillbridge-app --source . --region us-central1 --service-account skillbridge-streamlit@YOUR_PROJECT_ID.iam.gserviceaccount.com --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_LOCATION=us-central1,DATASTORE_ID=YOUR_FULL_DATASTORE_ID --allow-unauthenticated --memory 1Gi --timeout 300
```

---

## 🤖 Agent Pipeline

```
ResumeParser  →  GapAnalyst  →  CareerCoach  →  InterviewCoach
     ↓               ↓               ↓                ↓
parsed_skills   skill_gaps     career_roadmap   interview_questions
```

Each agent stores its output in shared session state via `output_key`, which the next agent reads automatically.

---

## 🛡️ Fallback Strategy

If AI is unavailable, the app automatically falls back to:

- **Keyword-based skill extraction** from 30+ common tech terms
- **Template roadmap** with Coursera/YouTube search suggestions
- Clear warning messages shown to the user

---

## 🗂️ Synthetic Dataset

The `data/` folder contains the following files:

- **`synthetic_jobs.csv`** — Original structured dataset with 100 synthetic job role entries including required skills, certifications, experience levels, and salary ranges
- **`synthetic_jobs.jsonl`** — Same 100 entries in JSONL format (one JSON object per line)
- **`job_catalog_unstructured.txt`** — The actual file loaded into Vertex AI Search datastore. Contains the same 100 job role samples converted to unstructured plain text format. Structured formats (CSV/JSONL) were attempted first but caused ingestion issues with the Discovery Engine, so the data was converted to unstructured text which loaded successfully.

All data is fully synthetic — no real personal or company information is included.

---

## 📐 Design Decisions & Tradeoffs

| Decision           | Chosen Approach                | Tradeoff                                     |
| ------------------ | ------------------------------ | -------------------------------------------- |
| Agent architecture | Sequential 4-agent pipeline    | More API calls but cleaner, focused outputs  |
| Role input         | Free text instead of dropdown  | More flexible but relies on fuzzy matching   |
| Data storage       | In-memory session only         | No privacy risk but no persistence           |
| Fallback           | Rule-based keyword matching    | Always works but less personalized than AI   |
| Deployment         | Cloud Run over Streamlit Cloud | Full GCP integration but more setup required |

---

## 👤 Author

**Ahraz Khan** — [GitHub](https://github.com/AhrazKhan31)
