# 🚀 SkillBridge Career Navigator

> An AI-powered multi-agent career coaching app that analyzes your resume, identifies skill gaps, and generates a personalized 8-week learning roadmap with curated course links and interview preparation.

---

## 🔗 Live Demo

**[ https://skillbridge-app-537062195130.us-central1.run.app](https://skillbridge-app-537062195130.us-central1.run.app)**

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
├── app.py                          # Streamlit frontend + AI runner
├── Dockerfile                      # Container configuration
├── requirements.txt                # Python dependencies
├── tests.py                        # Happy path + edge case tests
├── README.md                       # Project documentation
├── .env.example                    # Environment variable template
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git exclusions
├── data/
│   ├── synthetic_jobs.csv          # Synthetic jobs dataset
│   ├── synthetic_jobs.jsonl        # Synthetic jobs dataset (JSONL format)
│   └── job_catalog_unstructured.txt # Unstructured job catalog data
└── my_agent/
    ├── __init__.py
    ├── agent.py                    # 4-agent pipeline definition
    └── .env.example                # Agent env variable template
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.11+
- Google Cloud SDK installed
- GCP project with Vertex AI and Discovery Engine APIs enabled

### 1. Clone the repo

```bash
git clone https://github.com/AhrazKhan31/skill-bridge-career-navigator.git
cd skill-bridge-career-navigator
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in your values
```

Your `.env` should contain:

```env
GCP_PROJECT_ID=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_LOCATION=us-central1
DATASTORE_ID=projects/your-project-id/locations/global/collections/default_collection/dataStores/your-datastore-id
```

Also create `my_agent/.env` with the same values.

### 5. Authenticate with GCP

```bash
gcloud auth application-default login
```

### 6. Run the app

```bash
streamlit run app.py
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

## ⚠️ Known Limitations

- Free tier Vertex AI quota may cause rate limit errors (429) under heavy use
- Scanned/image-based PDFs may not parse correctly
- Roadmap URLs from Google Search may occasionally be outdated

---

## 🔮 Future Enhancements

- User accounts with saved history (Firebase Auth)
- LinkedIn profile URL parsing
- Progress tracker for roadmap completion
- PDF export of roadmap
- Live job board integration

---

## 🗂️ Synthetic Dataset

A sample job catalog CSV is included at `data/job_catalog_sample.csv` with 12 roles, their required skills, certifications, experience levels, and salary ranges. This represents the kind of data loaded into the Vertex AI Search datastore.

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
