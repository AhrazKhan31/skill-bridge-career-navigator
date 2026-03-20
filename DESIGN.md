# SkillBridge Career Navigator — Design Documentation

## 1. Problem Statement

Job seekers struggle to identify exactly which skills they are missing for their target roles. Generic job descriptions are hard to parse, and building a personalized learning roadmap requires hours of manual research. SkillBridge automates this entire process using a multi-agent AI pipeline.

---

## 2. System Architecture

```
User (Browser)
     │
     ▼
Streamlit Frontend (app.py)
     │
     ▼
SequentialAgent Pipeline (Google ADK)
     │
     ├── Agent 1: ResumeParser
     │     └── Extracts skills from uploaded PDF
     │
     ├── Agent 2: GapAnalyst
     │     └── Searches Vertex AI Datastore for role requirements
     │     └── Compares user skills vs required skills
     │
     ├── Agent 3: CareerCoach
     │     └── Google Search for courses, certifications, articles
     │     └── Generates 8-week day-wise roadmap with URLs
     │
     └── Agent 4: InterviewCoach
           └── Generates 3 role-specific interview questions
```

---

## 3. Tech Stack

| Layer               | Technology                          | Purpose                              |
| ------------------- | ----------------------------------- | ------------------------------------ |
| **Frontend**        | Streamlit                           | Web UI, file upload, results display |
| **Agent Framework** | Google ADK (Agent Development Kit)  | Multi-agent orchestration            |
| **LLM**             | Gemini 2.5 Flash Lite (Vertex AI)   | Powers all 4 agents                  |
| **Search**          | Vertex AI Search (Discovery Engine) | Job catalog lookup                   |
| **Web Search**      | Google Search Tool (ADK)            | Course and certification lookup      |
| **PDF Parsing**     | PyPDF2                              | Resume text extraction               |
| **Auth**            | Google Cloud IAM + Service Account  | Secure GCP access                    |
| **Deployment**      | Google Cloud Run                    | Serverless container hosting         |
| **Container**       | Docker                              | Packaging and deployment             |
| **Version Control** | GitHub                              | Source code management               |

---

## 4. Core Flow

```
1. User uploads PDF resume
2. User enters target role (free text)
3. ResumeParser extracts technical skills → saved to session state
4. GapAnalyst searches job catalog → identifies missing skills
5. CareerCoach searches web → builds 8-week roadmap with links
6. InterviewCoach → generates 3 interview questions
7. Results displayed with search/filter and update functionality
```

---

## 5. Key Design Decisions

### Multi-Agent over Single Prompt

Each agent has a single focused responsibility. This improves output quality — a dedicated GapAnalyst performs better than asking one model to do everything at once.

### SequentialAgent with Shared Session State

Agents pass data via `output_key` → `session.state`. Each agent reads the previous agent's output automatically, creating a clean pipeline without manual data passing.

### Rule-Based Fallback

If any AI agent fails (rate limit, timeout, outage), the app falls back to keyword-based skill extraction and a template roadmap. This ensures the app never shows a blank screen.

### Free-Text Role Input

Instead of a dropdown of fixed roles, users can type any role. The GapAnalyst finds the closest match in the catalog, making the app flexible for niche or emerging roles.

---

## 6. Data Flow

```
resume_text (PDF)  ──► ResumeParser ──► parsed_skills
target_role (text) ──┐
                     ├──► GapAnalyst ──► skill_gaps
parsed_skills ───────┘
skill_gaps ──────────────► CareerCoach ──► career_roadmap
career_roadmap ──────────► InterviewCoach ──► interview_questions
target_role ─────────────┘
```

---

## 7. Fallback Strategy

| Failure Point                       | Fallback Behavior                               |
| ----------------------------------- | ----------------------------------------------- |
| AI skill extraction returns empty   | Keyword matching against 30+ common tech skills |
| AI roadmap generation returns empty | Template 8-week roadmap per skill gap           |
| Full AI pipeline unavailable        | Complete rule-based results shown with warning  |
| PDF unreadable                      | Clear error message, user prompted to re-upload |

---

## 8. Future Enhancements

### Short Term (1-3 months)

- **User Accounts** — Save and revisit past analyses with Firebase Auth
- **Progress Tracker** — Mark roadmap items as complete, track % done
- **Export to PDF** — Download the roadmap as a formatted PDF
- **Email Roadmap** — Send the roadmap to user's email via SendGrid

### Medium Term (3-6 months)

- **LinkedIn Integration** — Parse LinkedIn profile URL instead of PDF upload
- **Job Board Integration** — Pull live job postings from LinkedIn/Indeed API and match against user skills
- **Peer Comparison** — Anonymous benchmarking against others targeting the same role
- **Multi-language Support** — Resume parsing and roadmap in Hindi, Spanish, etc.

### Long Term (6-12 months)

- **Mentor Matching** — Connect users with mentors who have the skills they need
- **Course Completion Tracking** — Integrate with Coursera/Udemy APIs to track actual progress
- **Salary Negotiation Coach** — Additional agent that advises on salary based on skill gaps closed
- **Mobile App** — React Native app wrapping the same backend

---

## 9. Known Limitations

- **Vertex AI quota** — Free tier has rate limits; heavy usage may hit 429 errors
- **Resume format** — Works best with text-based PDFs; scanned image PDFs may not parse correctly
- **Job catalog** — Currently limited to roles in the Vertex AI Search datastore; niche roles fall back to similarity matching
- **Roadmap URLs** — Google Search tool finds real URLs but they may occasionally be outdated

---

## 10. Security Considerations

- No user data is stored persistently — all processing is in-memory per session
- PDF content is never logged or saved
- GCP credentials managed via IAM service accounts, never hardcoded
- `.env` files gitignored, secrets managed via Cloud Run environment variables
