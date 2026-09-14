"""
Scoutly — Discovery Service (Playwright-based web scraping + LLM parsing)
"""

import hashlib
import asyncio
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from app.config import REQUEST_DELAY_SECONDS, DEFAULT_SOURCE_URLS
from app.database import fetch_all, fetch_one, execute_insert, get_db
from app.services.llm_client import llm_client
from app.prompts.parse_opportunity import PARSE_OPPORTUNITY_PROMPT

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    """Generate a SHA256 hash of a URL for deduplication."""
    return hashlib.sha256(url.strip().lower().encode()).hexdigest()


async def _check_robots_txt(url: str) -> bool:
    """Check if we're allowed to scrape the given URL per robots.txt."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        def _parse():
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch("*", url)

        # RobotFileParser does blocking network I/O — keep it off the event loop.
        return await asyncio.to_thread(_parse)
    except Exception as e:
        # If robots.txt can't be fetched/parsed, fail open rather than blocking
        # discovery entirely, but log it so it's visible.
        logger.warning(f"Could not check robots.txt for {url}: {e}")
        return True


async def _scrape_page(url: str, browser=None) -> str | None:
    """Scrape a page using Anakin's URL Scraper App."""
    try:
        import httpx
        import asyncio
        from app.config import ANAKIN_API_KEY
        
        if not ANAKIN_API_KEY:
            logger.warning("ANAKIN_API_KEY is not set. Cannot use Anakin scraper.")
            return None

        headers = {
            "X-API-Key": ANAKIN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "country": "us",
            "formats": ["markdown", "cleanedHtml"],
            # Devpost/MLH/Devfolio render their listings client-side (React SPAs).
            # Without useBrowser, Anakin does a plain HTTP fetch and gets back an
            # empty shell with no opportunity data — the LLM then has nothing to
            # parse, which is why discovery was silently returning 0 results.
            "useBrowser": True,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1) Submit the scrape job
            submit_resp = await client.post("https://api.anakin.io/v1/url-scraper", headers=headers, json=payload)
            submit_resp.raise_for_status()
            job = submit_resp.json()
            
            job_id = job.get("jobId")
            if not job_id:
                logger.error(f"Failed to get jobId from Anakin for {url}: {job}")
                return None
                
            # 2) Poll until the job finishes
            for _ in range(60):
                poll_resp = await client.get(f"https://api.anakin.io/v1/url-scraper/{job_id}", headers=headers)
                poll_resp.raise_for_status()
                result = poll_resp.json()
                
                status = result.get("status")
                if status == "completed":
                    # Extract the scraped content from top level
                    content = result.get("markdown", "")
                    if not content:
                        content = result.get("cleanedHtml", "")
                    if not content:
                        content = str(result)
                        
                    # Truncate very long pages to avoid Groq token limits (approx 4000 tokens)
                    if len(content) > 15000:
                        content = content[:15000] + "\n\n[... content truncated ...]"
                        
                    return content
                elif status == "failed":
                    logger.error(f"Anakin scraper failed for {url}: {result}")
                    return None
                    
                await asyncio.sleep(2)
            
            logger.error(f"Anakin scraper timed out for {url}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to scrape {url} with Anakin API: {e}")
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
    1. Visit each source URL with httpx
    2. Parse page text with LLM
    3. Deduplicate and store new opportunities

    Returns summary of results.
    """
    sources = source_urls or DEFAULT_SOURCE_URLS
    total_scraped = 0
    new_count = 0
    errors = []

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
        page_text = await _scrape_page(url)
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

    result = {
        "status": "completed",
        "new_opportunities": new_count,
        "total_scraped": total_scraped,
        "errors": errors
    }
    logger.info(f"Discovery complete: {result}")
    return result
