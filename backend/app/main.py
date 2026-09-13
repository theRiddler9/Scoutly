"""
Scoutly — FastAPI Application Entry Point
"""

import json
import logging
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Fix for Playwright NotImplementedError on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.config import FRONTEND_URL, SCREENSHOTS_DIR
from app.database import init_db, fetch_one, fetch_all
from app.services.scheduler import start_scheduler, stop_scheduler
from app.routes import profile, opportunities, applications, discovery

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scoutly")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Scoutly starting up...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Ensure screenshots directory
    Path(SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)

    # Start scheduler
    start_scheduler()
    logger.info("✅ Scheduler started")

    yield

    # Shutdown
    stop_scheduler()
    logger.info("🛑 Scoutly shutting down")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Scoutly",
    description="AI-powered Grant/Hackathon Scout & Auto-Applier",
    version="1.0.0",
    lifespan=lifespan,
)

from fastapi.responses import JSONResponse
from fastapi import Request
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    with open("error_log.txt", "w", encoding="utf-8") as f:
        f.write(error_msg)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "error": str(exc)})

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for screenshots
screenshots_path = Path(SCREENSHOTS_DIR)
screenshots_path.mkdir(parents=True, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_path)), name="screenshots")

@app.get("/demo-form")
async def demo_form():
    """A dummy hackathon registration form for the demo video (no login required)."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RevenueCat Shipaton 2026 - Registration</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0f111a; color: white; padding: 40px; }
            .container { max-w-2xl; margin: 0 auto; background: #1a1d27; padding: 30px; border-radius: 12px; }
            .field { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 500; color: #bac8ff; }
            input, textarea, select { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #2f3342; background: #0f111a; color: white; }
            button { background: #4c6ef5; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color: #bac8ff; margin-bottom: 5px;">RevenueCat Shipaton 2026</h1>
            <p style="color: #8c9bba; margin-bottom: 30px;">Official Registration Form</p>
            
            <form id="apply-form">
                <div class="field">
                    <label for="fullName">Full Name *</label>
                    <input type="text" id="fullName" name="fullName" required>
                </div>
                <div class="field">
                    <label for="emailAddr">Email Address *</label>
                    <input type="email" id="emailAddr" name="emailAddr" required>
                </div>
                <div class="field">
                    <label for="github">GitHub Profile URL</label>
                    <input type="url" id="github" name="github">
                </div>
                <div class="field">
                    <label for="skills">Primary Technologies & Skills</label>
                    <input type="text" id="skills" name="skills" placeholder="e.g. React, Python, AI">
                </div>
                <div class="field">
                    <label for="experience">Why do you want to participate?</label>
                    <textarea id="experience" name="experience" rows="4"></textarea>
                </div>
                <div class="field">
                    <label for="team">Are you looking for a team?</label>
                    <select id="team" name="team">
                        <option value="yes">Yes, I need a team</option>
                        <option value="no">No, I have a team / Solo</option>
                    </select>
                </div>
                <button type="submit">Submit Application</button>
            </form>
        </div>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(profile.router)
app.include_router(opportunities.router)
app.include_router(applications.router)
app.include_router(discovery.router)


@app.get("/")
async def root():
    """API health check."""
    return {
        "name": "Scoutly",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered Grant/Hackathon Scout & Auto-Applier",
    }


@app.get("/api/dashboard/stats")
async def dashboard_stats():
    """Get dashboard overview statistics."""
    total_opps = await fetch_one("SELECT COUNT(*) as count FROM opportunities")
    matched_opps = await fetch_one(
        "SELECT COUNT(*) as count FROM opportunities WHERE status = 'matched'"
    )
    pending_approvals = await fetch_one(
        "SELECT COUNT(*) as count FROM applications WHERE status = 'awaiting_approval'"
    )
    submitted = await fetch_one(
        "SELECT COUNT(*) as count FROM applications WHERE status = 'submitted'"
    )
    avg_score = await fetch_one(
        "SELECT AVG(score) as avg FROM matches WHERE score > 0"
    )

    # Upcoming deadlines (next 7 days)
    upcoming = await fetch_all(
        """SELECT o.id, o.name, o.deadline, m.score
           FROM opportunities o
           LEFT JOIN matches m ON o.id = m.opportunity_id
           WHERE o.deadline != 'TBD'
             AND o.deadline >= date('now')
             AND o.deadline <= date('now', '+7 days')
           ORDER BY o.deadline ASC
           LIMIT 5"""
    )

    return {
        "total_opportunities": total_opps["count"] if total_opps else 0,
        "matched_opportunities": matched_opps["count"] if matched_opps else 0,
        "pending_approvals": pending_approvals["count"] if pending_approvals else 0,
        "submitted_applications": submitted["count"] if submitted else 0,
        "avg_match_score": round(avg_score["avg"], 1) if avg_score and avg_score["avg"] else 0,
        "upcoming_deadlines": upcoming,
    }
