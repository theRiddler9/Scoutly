"""
Scoutly — Opportunity Routes
"""

import json
from fastapi import APIRouter, HTTPException, Query
from app.database import fetch_all, fetch_one
from app.services.matcher import run_matching
from app.models import MatchTriggerRequest

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


@router.get("")
async def list_opportunities(
    profile_id: int = Query(1, description="Profile ID for match scores"),
    sort_by: str = Query("score", description="Sort by: score, deadline, discovered_at"),
    status: str = Query(None, description="Filter by status: found, matched, archived"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all opportunities with optional match scores."""
    # Build query with LEFT JOIN to include match data
    query = """
        SELECT o.*,
               m.score as match_score,
               m.qualifies,
               m.reasoning as match_reasoning,
               m.deadline_feasible
        FROM opportunities o
        LEFT JOIN matches m ON o.id = m.opportunity_id AND m.profile_id = ?
    """
    params = [profile_id]

    if status:
        query += " WHERE o.status = ?"
        params.append(status)

    # Sort
    sort_map = {
        "score": "COALESCE(m.score, 0) DESC",
        "deadline": "o.deadline ASC",
        "discovered_at": "o.discovered_at DESC",
        "name": "o.name ASC",
    }
    order = sort_map.get(sort_by, "COALESCE(m.score, 0) DESC")
    query += f" ORDER BY {order}"
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    opportunities = await fetch_all(query, tuple(params))

    # Parse JSON fields
    for opp in opportunities:
        opp["tags"] = json.loads(opp.get("tags", "[]"))
        opp["qualifies"] = bool(opp.get("qualifies")) if opp.get("qualifies") is not None else None
        opp["deadline_feasible"] = bool(opp.get("deadline_feasible")) if opp.get("deadline_feasible") is not None else None

    # Get total count
    count_query = "SELECT COUNT(*) as total FROM opportunities"
    count_params = ()
    if status:
        count_query += " WHERE status = ?"
        count_params = (status,)
    count_result = await fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    return {
        "total": total,
        "opportunities": opportunities,
    }


@router.get("/{opportunity_id}")
async def get_opportunity(opportunity_id: int, profile_id: int = Query(1)):
    """Get a single opportunity with match details."""
    opp = await fetch_one(
        """SELECT o.*,
                  m.score as match_score,
                  m.qualifies,
                  m.reasoning as match_reasoning,
                  m.deadline_feasible
           FROM opportunities o
           LEFT JOIN matches m ON o.id = m.opportunity_id AND m.profile_id = ?
           WHERE o.id = ?""",
        (profile_id, opportunity_id),
    )
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    opp["tags"] = json.loads(opp.get("tags", "[]"))
    opp["qualifies"] = bool(opp.get("qualifies")) if opp.get("qualifies") is not None else None
    opp["deadline_feasible"] = bool(opp.get("deadline_feasible")) if opp.get("deadline_feasible") is not None else None
    return opp


@router.post("/match")
async def trigger_matching(request: MatchTriggerRequest):
    """Trigger LLM-based matching for opportunities against a profile."""
    result = await run_matching(
        profile_id=request.profile_id,
        opportunity_ids=request.opportunity_ids,
    )
    return result

@router.delete("/clear")
async def clear_all_opportunities():
    """Clear all opportunities, matches, applications, and logs."""
    from app.database import execute_update
    await execute_update("DELETE FROM field_logs")
    await execute_update("DELETE FROM applications")
    await execute_update("DELETE FROM matches")
    await execute_update("DELETE FROM opportunities")
    return {"status": "success", "message": "All opportunities and related data cleared"}
