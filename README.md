# SkillPath AI 🎓

An AI-powered personalized learning platform that accelerates technical career transitions through a specialized multi-agent architecture.

---

## 🌟 Tech Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **LLM & Reasoning Engine:** [Google Gemini API](https://ai.google.dev/) (`google-generativeai`)
- **Database & Persistence:** [Supabase](https://supabase.com/) (PostgreSQL)
- **Styling:** Custom CSS with clean cards, badges, and responsive layout
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

```text
SkillPath-AI/
├── .env.example              # Template for API keys and configuration
├── .gitignore                 # Excludes virtual envs, secrets, and cache
├── README.md                  # Project documentation & setup instructions
├── requirements.txt           # Python dependencies
├── app.py                     # Main Streamlit application entrypoint
│
├── agents/                    # Multi-agent core logic
│   ├── __init__.py
│   ├── skill_gap_agent.py     # Analyzes current vs required skills
│   ├── career_agent.py        # Generates phased milestones & roadmaps
│   ├── recommendation_agent.py# Curates tailored resources (docs, courses, projects)
│   ├── progress_agent.py      # Tracks completion velocity & pacing
│   └── mentor_agent.py        # Conversational AI mentor & code explainer
│
├── database/                  # Database connectivity & data access
│   ├── __init__.py
│   └── supabase_client.py     # Resilient Supabase client with offline fallback
│
├── utils/                     # Shared utilities
│   ├── __init__.py
│   └── helpers.py             # CSS loader, Gemini initializer, JSON parsers
│
└── assets/                    # Static assets & styles
    └── style.css              # Custom UI enhancements for Streamlit
```

---

## 🤖 The 5 Specialized Agents

1. **Skill Gap Agent (`skill_gap_agent.py`)**:
   - Takes a learner's current skillset and target job title.
   - Evaluates industry benchmarks to determine missing competencies, prerequisite gaps, and readiness score.
2. **Career Agent (`career_agent.py`)**:
   - Converts gaps into phased, time-bound learning roadmaps (e.g., 8-12 weeks).
   - Generates weekly objectives, realistic hourly commitments, and milestone targets.
3. **Recommendation Agent (`recommendation_agent.py`)**:
   - Suggests high-quality learning resources (documentation, interactive labs, video courses, open-source projects) matched to user preferences (hands-on vs theory, free vs paid).
4. **Progress Agent (`progress_agent.py`)**:
   - Tracks completed milestones and projects.
   - Computes completion velocity and provides adaptive pacing advice.
5. **Mentor Agent (`mentor_agent.py`)**:
   - Offers an on-demand AI tutor to clarify doubts, review code, and provide conceptual analogies.

---

## 🚀 Getting Started

### 1. Clone & Navigate to Project
```bash
git clone https://github.com/your-username/SkillPath-AI.git
cd SkillPath-AI
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to create `.env`:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux / Bash
cp .env.example .env
```
Edit `.env` with your credentials:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_public_key_here
```

> **Note:** The application is resilient. If you do not have Gemini or Supabase credentials yet, it will safely run in **Demo / Offline Mode** without crashing.

### 5. Run the Application
```bash
streamlit run app.py
```

---

## 🗄️ Supabase Database Schema (Optional Reference)

When you are ready to persist data to Supabase, run this script in the Supabase SQL Editor:

```sql
-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    name TEXT,
    target_role TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Learning Paths Table
CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    path_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. User Progress Table
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    milestone_id TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🛡️ Security Best Practices
- Never commit `.env` or your API keys to GitHub.
- `.gitignore` is already pre-configured to exclude sensitive credentials and build artifacts.
- The app uses client-side environment variable masking to prevent accidental credential leakage.
