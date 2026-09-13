"""
Scoutly — Configuration & Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "scoutly.db"))
SCREENSHOTS_DIR = os.getenv("SCREENSHOTS_DIR", str(BASE_DIR / "screenshots"))

# Ensure screenshots directory exists
Path(SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────────────
ANAKIN_API_KEY = os.getenv("ANAKIN_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── LLM Settings ──────────────────────────────────────────────────────────────
LLM_MODEL = "qwen/qwen3.8-27b"
LLM_TEMPERATURE = 0.2
LLM_MAX_RETRIES = 3
LLM_RETRY_BASE_DELAY = 2  # seconds, exponential backoff base

# ── Discovery Settings ────────────────────────────────────────────────────────
DISCOVERY_INTERVAL_MINUTES = int(os.getenv("DISCOVERY_INTERVAL_MINUTES", "60"))
REQUEST_DELAY_SECONDS = 1.5  # delay between scraping requests

# Default source URLs for discovery
DEFAULT_SOURCE_URLS = [
    {
        "name": "Devpost Hackathons",
        "url": "https://devpost.com/hackathons?status[]=upcoming&status[]=open",
        "type": "devpost"
    },
    {
        "name": "MLH Events",
        "url": "https://mlh.io/seasons/2025/events",
        "type": "mlh"
    },
    {
        "name": "Devfolio Hackathons",
        "url": "https://devfolio.co/hackathons",
        "type": "devfolio"
    },
]

# ── CORS ──────────────────────────────────────────────────────────────────────
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
