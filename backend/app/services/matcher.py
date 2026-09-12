"""
Scoutly — Matcher Service (Profile-Opportunity Matching via LLM)
"""

import json
import logging
from datetime import datetime, timezone
from app.database import fetch_all, fetch_one, execute_insert, get_db
from app.services.llm_client import llm_client
from app.prompts.match_profile import MATCH_PROFILE_PROMPT

logger = logging.getLogger(__name__)


async def _get_profile(profile_id: int) -> dict | None:
    """Fetch a user profile and parse its JSON fields."""
    profile = await fetch_one("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    if not profile:
        return None

    # Parse JSON fields
    profile["skills"] = json.loads(profile.get("skills", "[]"))
    profile["projects"] = json.loads(profile.get("projects", "[]"))
    profile["social_handles"] = json.loads(profile.get("social_handles", "{}"))
    return profile


async def _match_single(profile: dict, opportunity: dict) -> dict:
    """
    Match a single opportunity against a profile using the LLM.

    Returns the match result dict.
    """
    # Build the payload
    payload = {
        "profile": {
            "name": profile["name"],
            "skills": profile["skills"],
            "projects": profile["projects"],
            "github_url": profile["github_url"],
            "resume_summary": profile.get("resume_text", "")[:2000],  # Truncate if long
        },
        "opportunity": {
            "name": opportunity["name"],
            "eligibility_summary": opportunity["eligibility_summary"],
            "description": opportunity["description"],
            "deadline": opportunity["deadline"],
            "prize_info": opportunity["prize_info"],
            "tags": json.loads(opportunity.get("tags", "[]")),
        },
        "current_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    try:
        result = await llm_client.call(
            system_prompt=MATCH_PROFILE_PROMPT,
            user_payload=payload,
            json_mode=True,
        )

        return {
            "qualifies": bool(result.get("qualifies", False)),
            "score": int(result.get("score", 0)),
            "reasoning": result.get("reasoning", ""),
            "deadline_feasible": bool(result.get("deadline_feasible", True)),
            "key_strengths": result.get("key_strengths", []),
            "gaps": result.get("gaps", []),
        }
    except Exception as e:
        logger.error(f"Matching failed for opportunity {opportunity['id']}: {e}")
        return {
            "qualifies": False,
            "score": 0,
            "reasoning": f"Matching failed: {str(e)}",
            "deadline_feasible": True,
            "key_strengths": [],
            "gaps": [],
        }


async def run_matching(profile_id: int = 1, opportunity_ids: list[int] | None = None) -> dict:
    """
    Run matching for a profile against opportunities.

    Args:
        profile_id: The profile to match against
        opportunity_ids: Specific opportunities to match (None = all unmatched)

    Returns:
        Summary of matching results
    """
    profile = await _get_profile(profile_id)
    if not profile:
        return {"status": "error", "message": f"Profile {profile_id} not found", "matches": []}

    # Get opportunities to match
    if opportunity_ids:
        placeholders = ",".join("?" * len(opportunity_ids))
        opportunities = await fetch_all(
            f"SELECT * FROM opportunities WHERE id IN ({placeholders})",
            tuple(opportunity_ids),
        )
    else:
        # Get all opportunities not yet matched for this profile
        opportunities = await fetch_all(
            """SELECT o.* FROM opportunities o
               WHERE o.id NOT IN (
                   SELECT opportunity_id FROM matches WHERE profile_id = ?
               )
               ORDER BY o.discovered_at DESC""",
            (profile_id,),
        )

    if not opportunities:
        return {"status": "completed", "message": "No new opportunities to match", "matches": []}

    logger.info(f"Matching {len(opportunities)} opportunities for profile {profile_id}")
    matches = []
    matched_count = 0

    for opp in opportunities:
        result = await _match_single(profile, opp)

        # Build reasoning with strengths/gaps
        full_reasoning = result["reasoning"]
        if result.get("key_strengths"):
            full_reasoning += f"\n\nStrengths: {', '.join(result['key_strengths'])}"
        if result.get("gaps"):
            full_reasoning += f"\nGaps: {', '.join(result['gaps'])}"

        # Store match in database
        try:
            match_id = await execute_insert(
                """INSERT OR REPLACE INTO matches
                   (profile_id, opportunity_id, qualifies, score, reasoning, deadline_feasible)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    profile_id,
                    opp["id"],
                    1 if result["qualifies"] else 0,
                    result["score"],
                    full_reasoning,
                    1 if result["deadline_feasible"] else 0,
                ),
            )

            # Update opportunity status
            db = await get_db()
            try:
                await db.execute(
                    "UPDATE opportunities SET status = 'matched' WHERE id = ?",
                    (opp["id"],),
                )
                await db.commit()
            finally:
                await db.close()

            matches.append({
                "match_id": match_id,
                "opportunity_id": opp["id"],
                "opportunity_name": opp["name"],
                "score": result["score"],
                "qualifies": result["qualifies"],
                "reasoning": full_reasoning,
            })
            matched_count += 1

        except Exception as e:
            logger.error(f"Failed to store match for opportunity {opp['id']}: {e}")

    # Sort by score descending
    matches.sort(key=lambda m: m["score"], reverse=True)

    return {
        "status": "completed",
        "matched": matched_count,
        "total_opportunities": len(opportunities),
        "matches": matches,
    }
