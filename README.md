<div align="center">

# 🚀 Scoutly

### AI-Powered Grant, Hackathon & Fellowship Scout with Auto-Application

*Discover opportunities. Get AI-matched. Auto-fill applications. Stay in control.*

[![Built for Anakin Forge](https://img.shields.io/badge/Built%20for-Anakin%20Forge%20Hackathon-blueviolet?style=for-the-badge)](https://anakin.io)
[![Powered by Anakin](https://img.shields.io/badge/Powered%20by-Anakin%20API%20%2B%20Qwen-orange?style=for-the-badge)](https://anakin.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## What is Scoutly?

Scoutly is an **AI agent** that automates the tedious process of finding and applying to hackathons, grants, and fellowships. It:

1. **Discovers** open opportunities from Devpost, MLH, Devfolio, and custom sources using blazing fast HTTP scraping.
2. **Matches** them to your profile using AI reasoning (Anakin Forge API).
3. **Auto-fills** application forms via browser automation (Playwright).
4. **Stops before submitting** — you always have final say with screenshot preview.

> **Built for [Anakin Forge Hackathon](https://anakin.io)** — demonstrating the power of AI agents for real-world automation.

---

## Features

| Feature | Description |
|---------|-------------|
| **Smart Discovery** | Ultra-fast `httpx` scraping of hackathon platforms with LLM-based content parsing |
| **AI Matching** | Profile-opportunity matching with 0-100 score, reasoning, and gap analysis via Anakin Forge |
| **Form Auto-Fill** | Intelligent form field detection and auto-population from your profile via Playwright |
| **Human-in-the-Loop** | Screenshot preview & explicit approval before any submission |
| **Dashboard** | Real-time status tracking with glassmorphism dark UI |
| **Scheduled Discovery** | APScheduler runs periodic scans to catch new opportunities |
| **Full Audit Log** | Every field filled is logged with reasoning for transparency |

---

## Architecture

```text
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
│  │              Anakin Forge API (Qwen / Llama)       │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────┐  ┌──────────────────────────────┐    │
│  │   SQLite DB    │  │  Playwright (Form Filler)    │    │
│  └────────────────┘  └──────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Start (Local Demo)

If you are running the app for a video demo, **local execution is highly recommended** to bypass free-tier server limitations for browser automation.

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Anakin Forge API Key** 

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

# Install Playwright browsers (Required for Form Auto-Fill)
playwright install chromium

# Setup environment variables
copy .env.example .env
# Edit .env and add your ANAKIN_API_KEY
```

### 2. Setup Frontend

```bash
cd ../frontend
npm install
```

### 3. Run the Application

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

Visit **http://localhost:5173** in your browser.

---

## Production Deployment

### Backend (Render)
1. Deploy the `backend` folder as a **Web Service** on Render (Python 3.12).
2. Set the start command to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Environment Variables:
   - `ANAKIN_API_KEY`: Your API key
   - `PLAYWRIGHT_BROWSERS_PATH`: `0`
4. *Note: Playwright browser launching for the "Auto-Fill" feature requires a Docker deployment on Render to include necessary OS libraries.*

### Frontend (Vercel)
1. Deploy the `frontend` folder to Vercel.
2. Build command: `npm run build`
3. Output directory: `dist`
4. Environment Variables:
   - `VITE_API_URL`: Your Render backend URL (e.g. `https://scoutly-xyz.onrender.com`)

---

## Usage Guide

### Step 1: Create Your Profile
Navigate to the **Profile** page and fill in:
- Name, email, GitHub URL
- Skills & technologies (add as tags)
- 2-3 project descriptions with tech stacks
- Resume text / bio
- Social handles (Twitter, LinkedIn, website)

### Step 2: Discover Opportunities
Click **"Discover"** on the Dashboard to scan configured sources. The AI will:
- Fetch hackathon pages at lightning speed using HTTPX
- Extract and parse opportunity data with the Anakin LLM
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
- Click **"Approve & Submit"** or **"Manual Action Required"**

> **Scoutly NEVER submits without your explicit approval.**

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **LLM** | Anakin Forge API (`openai` SDK compatible) |
| **Scraping** | HTTPX (Discovery), Playwright (Form-filling) |
| **Database** | SQLite with aiosqlite |
| **Frontend** | React 18, Vite, Tailwind CSS v3 |
| **Icons** | Lucide React |

---

## Anakin Forge Hackathon

This project was built for the **Anakin Forge Hackathon** by [anakin.io](https://anakin.io).

It demonstrates how AI agents can automate real-world workflows while maintaining human oversight — the key principle being **"AI does the work, human makes the call."**

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---


