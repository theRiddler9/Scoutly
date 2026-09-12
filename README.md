<div align="center">

# 🚀 Scoutly

### AI-Powered Grant, Hackathon & Fellowship Scout with Auto-Application

*Discover opportunities. Get AI-matched. Auto-fill applications. Stay in control.*

[![Built for Anakin Forge](https://img.shields.io/badge/Built%20for-Anakin%20Forge%20Hackathon-blueviolet?style=for-the-badge)](https://anakin.io)
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq%20%2B%20Llama%203.3-orange?style=for-the-badge)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🎯 What is Scoutly?

Scoutly is an **AI agent** that automates the tedious process of finding and applying to hackathons, grants, and fellowships. It:

1. **Discovers** open opportunities from Devpost, MLH, Devfolio, and custom sources
2. **Matches** them to your profile using AI reasoning (Groq + Llama 3.3 70B)
3. **Auto-fills** application forms via browser automation (Playwright)
4. **Stops before submitting** — you always have final say with screenshot preview

> **Built for [Anakin Forge Hackathon](https://anakin.io)** — demonstrating the power of AI agents for real-world automation.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Discovery** | Playwright-powered scraping of hackathon platforms with LLM-based content parsing |
| 🧠 **AI Matching** | Profile-opportunity matching with 0-100 score, reasoning, and gap analysis |
| 🤖 **Form Auto-Fill** | Intelligent form field detection and auto-population from your profile |
| 🛡️ **Human-in-the-Loop** | Screenshot preview & explicit approval before any submission |
| 📊 **Dashboard** | Real-time status tracking with glassmorphism dark UI |
| 🔄 **Scheduled Discovery** | APScheduler runs periodic scans to catch new opportunities |
| 📝 **Full Audit Log** | Every field filled is logged with reasoning for transparency |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React Dashboard                        │
│              (Vite + Tailwind v3 + Lucide)               │
└──────────────┬───────────────────────────────────────────┘
               │ REST API
┌──────────────▼───────────────────────────────────────────┐
│                    FastAPI Backend                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Profile  │  │Discovery │  │ Matcher  │  │FormFiller│ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│       │              │             │             │        │
│  ┌────▼──────────────▼─────────────▼─────────────▼────┐  │
│  │              Groq LLM (Llama 3.3 70B)              │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────┐  ┌──────────────────────────────┐    │
│  │   SQLite DB    │  │  Playwright (Headless Chrome) │    │
│  └────────────────┘  └──────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Groq API Key** (free — [sign up at console.groq.com](https://console.groq.com))

### 1. Clone & Setup Backend

```bash
# Clone the repo
git clone https://github.com/your-username/scoutly.git
cd scoutly

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Setup environment variables
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Setup Frontend

```bash
cd ../frontend
npm install
```

### 3. Configure API Key

Edit `backend/.env`:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Open the Dashboard

Visit **http://localhost:5173** in your browser.

---

## 📖 Usage Guide

### Step 1: Create Your Profile
Navigate to the **Profile** page and fill in:
- Name, email, GitHub URL
- Skills & technologies (add as tags)
- 2-3 project descriptions with tech stacks
- Resume text / bio
- Social handles (Twitter, LinkedIn, website)

### Step 2: Discover Opportunities
Click **"Discover"** on the Dashboard to scan configured sources. The AI will:
- Visit each source URL via headless browser
- Extract and parse opportunity data with LLM
- De-duplicate and store new findings

### Step 3: Match & Rank
Click **"Match All"** to have the AI evaluate each opportunity against your profile. You'll see:
- **Score** (0-100) with color-coded ring
- **Reasoning** for the match assessment
- **Strengths** and **Gaps** analysis

### Step 4: Auto-Fill Applications
On any opportunity, click **"Auto-Fill"** to:
- Open the application form in a headless browser
- Detect all form fields (labels, types, options)
- Map your profile data to each field using AI
- Take a screenshot of the filled form

### Step 5: Review & Approve
On the **Applications** page:
- View the screenshot of the filled form
- Check the field-by-field fill log with reasoning
- Click **"Approve & Submit"** or **"Reject"**

> ⚠️ **Scoutly NEVER submits without your explicit approval.**

---

## 🛡️ Safety & Guardrails

| Guardrail | Implementation |
|-----------|---------------|
| **No auto-submit** | Form-filler stops before submit; requires explicit `POST /approve` |
| **robots.txt** | Checked via `urllib.robotparser` before any scraping |
| **Rate limiting** | 1.5s delay between requests; exponential backoff on LLM calls |
| **Full audit trail** | Every field logged with value + reasoning to `field_logs` table |
| **Error handling** | try/except with 3x retry (exponential backoff) on all Groq calls |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | POST | Create profile |
| `/api/profile/{id}` | GET/PUT/DELETE | CRUD profile |
| `/api/opportunities` | GET | List with match scores |
| `/api/opportunities/match` | POST | Trigger AI matching |
| `/api/discovery/run` | POST | Run discovery scan |
| `/api/applications/fill` | POST | Auto-fill a form |
| `/api/applications/{id}/screenshot` | GET | Get fill screenshot |
| `/api/applications/{id}/approve` | POST | Approve & submit |
| `/api/applications/{id}/field-logs` | GET | View field fill log |
| `/api/dashboard/stats` | GET | Dashboard statistics |

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **LLM** | Groq API (free tier), Llama 3.3 70B Versatile |
| **Browser Automation** | Playwright (headless Chromium) |
| **Database** | SQLite with aiosqlite |
| **Scheduler** | APScheduler |
| **Frontend** | React 18, Vite, Tailwind CSS v3 |
| **Icons** | Lucide React |
| **HTTP Client** | Axios |

---

## 🎬 Demo Script

For the hackathon submission demo (2-3 minutes):

1. **Profile Setup** (30s) — Show the profile form, fill in sample data
2. **Discovery** (30s) — Click Discover, watch opportunities populate
3. **Matching** (30s) — Click Match All, show scores and AI reasoning
4. **Auto-Fill** (45s) — Pick a top opportunity, click Auto-Fill, show the filled form screenshot
5. **Approval** (15s) — Review field logs, approve submission
6. **Confirmation** (15s) — Show the submitted status in the dashboard

---

## 🗺️ Next Steps / Roadmap

### Short Term
- [ ] **Gemini API Fallback** — Auto-switch to Gemini 2.0 Flash when Groq rate limit is hit
- [ ] **Resume PDF Upload** — Parse uploaded PDFs with text extraction
- [ ] **Email Notifications** — Send alerts for new high-match opportunities
- [ ] **Multi-Profile Support** — Support multiple user profiles for team applications

### Medium Term
- [ ] **OAuth Login** — Google/GitHub SSO for user authentication
- [ ] **Custom Source URLs** — UI to add/remove discovery sources from the dashboard
- [ ] **Batch Auto-Fill** — Fill multiple applications in one click
- [ ] **Application Templates** — Save and reuse field mappings for similar forms
- [ ] **Chrome Extension** — Browser extension for one-click "Scout this page"

### Long Term
- [ ] **Calendar Integration** — Sync deadlines to Google Calendar
- [ ] **Team Matching** — Find teammates based on complementary skills
- [ ] **Follow-Up Tracker** — Track post-submission status and interview scheduling
- [ ] **Analytics Dashboard** — Conversion rates, response rates, best-matching categories
- [ ] **Self-Hosted LLM** — Option to run with a local LLM (Ollama/vLLM) for privacy

---

## Project Structure

```
Scoutly/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # SQLite schema & helpers
│   │   ├── models.py            # Pydantic schemas
│   │   ├── routes/              # API endpoints
│   │   │   ├── profile.py
│   │   │   ├── opportunities.py
│   │   │   ├── applications.py
│   │   │   └── discovery.py
│   │   ├── services/            # Business logic
│   │   │   ├── llm_client.py    # Groq wrapper + retry
│   │   │   ├── discovery.py     # Web scraping
│   │   │   ├── matcher.py       # AI matching
│   │   │   ├── form_filler.py   # Form auto-fill
│   │   │   └── scheduler.py     # APScheduler
│   │   └── prompts/             # LLM system prompts
│   │       ├── parse_opportunity.py
│   │       ├── match_profile.py
│   │       └── fill_form.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css            # Global styles
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   └── ScoreRing.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── Opportunities.jsx
│   │   │   └── Applications.jsx
│   │   └── services/
│   │       └── api.js
│   ├── tailwind.config.js
│   └── package.json
├── screenshots/                 # Auto-filled form screenshots
├── README.md
└── .gitignore
```

---

## Anakin Forge Hackathon

This project was built for the **Anakin Forge Hackathon** by [anakin.io](https://anakin.io).

It demonstrates how AI agents can automate real-world workflows while maintaining human oversight — the key principle being **"AI does the work, human makes the call."**

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---


