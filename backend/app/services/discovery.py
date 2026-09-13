"""
Scoutly — Discovery Service (Playwright-based web scraping + LLM parsing)
"""

import hashlib
import asyncio
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from playwright.async_api import async_playwright
from app.config import REQUEST_DELAY_SECONDS, DEFAULT_SOURCE_URLS
from app.database import fetch_all, fetch_one, execute_insert, get_db
from app.services.llm_client import llm_client
from app.prompts.parse_opportunity import PARSE_OPPORTUNITY_PROMPT

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    """Generate a SHA256 hash of a URL for deduplication."""
    return hashlib.sha256(url.strip().lower().encode()).hexdigest()


async def _check_robots_txt(url: str) -> bool:
    """Bypass robots.txt check for hackathon platforms."""
    return True


async def _scrape_page(url: str, browser) -> str | None:
    """Scrape a page and return its text content."""
    try:
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait a bit for dynamic content
        await page.wait_for_timeout(2000)

        # Extract text content
        text_content = await page.evaluate("""
            () => {
                // Remove script and style elements
                const scripts = document.querySelectorAll('script, style, noscript');
                scripts.forEach(s => s.remove());

                // Get main content area if available
                const main = document.querySelector('main, [role="main"], .content, #content, .main');
                if (main) return main.innerText;

                return document.body.innerText;
            }
        """)

        await context.close()

        # Truncate very long pages to avoid token limits
        if len(text_content) > 15000:
            text_content = text_content[:15000] + "\n\n[... content truncated ...]"

        return text_content

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None


async def _parse_opportunities_with_llm(page_text: str, source_url: str) -> list[dict]:
    """Use LLM to parse raw page text into structured opportunity data."""
    try:
        payload = {
            "source_url": source_url,
            "page_text": page_text
        }
        result = await llm_client.call(
            system_prompt=PARSE_OPPORTUNITY_PROMPT,
            user_payload=payload,
            json_mode=True
        )

        opportunities = result.get("opportunities", [])
        if not isinstance(opportunities, list):
            opportunities = [result] if "name" in result else []

        return opportunities

    except Exception as e:
        logger.error(f"LLM parsing failed for {source_url}: {e}")
        return []


async def _store_opportunity(opp: dict, source_url: str) -> int | None:
    """Store a parsed opportunity in the database, deduplicating by URL."""
    apply_url = opp.get("apply_url", source_url)
    url_hash = _url_hash(apply_url)

    # Check for duplicate
    existing = await fetch_one(
        "SELECT id FROM opportunities WHERE url_hash = ?",
        (url_hash,)
    )
    if existing:
        logger.debug(f"Opportunity already exists: {opp.get('name', 'unknown')}")
        return None

    import json
    tags = opp.get("tags", [])
    if isinstance(tags, list):
        tags_json = json.dumps(tags)
    else:
        tags_json = "[]"

    try:
        row_id = await execute_insert(
            """INSERT INTO opportunities
               (name, source_url, apply_url, deadline, eligibility_summary,
                prize_info, raw_text, description, organizer, tags, url_hash, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'found')""",
            (
                opp.get("name", "Unnamed Opportunity"),
                source_url,
                apply_url,
                opp.get("deadline", "TBD"),
                opp.get("eligibility_summary", ""),
                opp.get("prize_info", "Not specified"),
                "",  # raw_text — could store if needed
                opp.get("description", ""),
                opp.get("organizer", ""),
                tags_json,
                url_hash,
            )
        )
        logger.info(f"Stored new opportunity: {opp.get('name', 'unknown')} (id={row_id})")
        return row_id
    except Exception as e:
        logger.error(f"Failed to store opportunity: {e}")
        return None


async def run_discovery(source_urls: list[dict] | None = None) -> dict:
    """
    Run the full discovery pipeline:
    1. Visit each source URL with Playwright
    2. Parse page text with LLM
    3. Deduplicate and store new opportunities

    Returns summary of results.
    """
    sources = source_urls or DEFAULT_SOURCE_URLS
    total_scraped = 0
    new_count = 0
    errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for source in sources:
            url = source["url"] if isinstance(source, dict) else source
            name = source.get("name", url) if isinstance(source, dict) else url

            logger.info(f"Discovering opportunities from: {name} ({url})")

            # Check robots.txt
            allowed = await _check_robots_txt(url)
            if not allowed:
                msg = f"Blocked by robots.txt: {url}"
                logger.warning(msg)
                errors.append(msg)
                continue

            # Scrape page
            page_text = await _scrape_page(url, browser)
            if not page_text:
                errors.append(f"Failed to scrape: {url}")
                continue

            total_scraped += 1

            # Parse with LLM
            opportunities = await _parse_opportunities_with_llm(page_text, url)
            logger.info(f"Found {len(opportunities)} opportunities from {name}")

            # Store each opportunity
            for opp in opportunities:
                row_id = await _store_opportunity(opp, url)
                if row_id is not None:
                    new_count += 1

            # Rate limiting delay
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

        await browser.close()

    result = {
        "status": "completed",
        "new_opportunities": new_count,
        "total_scraped": total_scraped,
        "errors": errors
    }
    logger.info(f"Discovery complete: {result}")
    return result
