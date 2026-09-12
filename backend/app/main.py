"""
Scoutly — FastAPI Application Entry Point
"""

import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for screenshots
screenshots_path = Path(SCREENSHOTS_DIR)
screenshots_path.mkdir(parents=True, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_path)), name="screenshots")

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
