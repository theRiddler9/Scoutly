"""
Scoutly — Scheduler Service (APScheduler for periodic discovery & matching)
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import DISCOVERY_INTERVAL_MINUTES

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _scheduled_discovery():
    """Run discovery and matching on schedule."""
    from app.services.discovery import run_discovery
    from app.services.matcher import run_matching

    logger.info("Scheduled discovery run starting...")
    try:
        result = await run_discovery()
        logger.info(f"Discovery result: {result}")

        if result.get("new_opportunities", 0) > 0:
            logger.info("Running matching for new opportunities...")
            match_result = await run_matching(profile_id=1)
            logger.info(f"Matching result: {match_result.get('matched', 0)} matches")
    except Exception as e:
        logger.error(f"Scheduled discovery failed: {e}")


def start_scheduler():
    """Start the background scheduler for periodic discovery."""
    scheduler.add_job(
        _scheduled_discovery,
        trigger=IntervalTrigger(minutes=DISCOVERY_INTERVAL_MINUTES),
        id="discovery_job",
        name="Periodic Discovery & Matching",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — discovery runs every {DISCOVERY_INTERVAL_MINUTES} minutes"
    )


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
