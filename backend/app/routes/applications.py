"""
Scoutly — Application Routes (Fill, Preview, Approve, Submit)
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.database import fetch_one, fetch_all, execute_update
from app.services.form_filler import fill_application, submit_application
from app.models import FillRequest, ApprovalRequest

router = APIRouter(prefix="/api/applications", tags=["Applications"])


@router.get("")
async def list_applications():
    """List all applications with their status and related opportunity info."""
    apps = await fetch_all(
        """SELECT a.*,
                  o.name as opportunity_name,
                  o.apply_url as opportunity_apply_url,
                  m.score as match_score
           FROM applications a
           JOIN matches m ON a.match_id = m.id
           JOIN opportunities o ON m.opportunity_id = o.id
           ORDER BY a.created_at DESC"""
    )

    for app in apps:
        app["form_data"] = json.loads(app.get("form_data", "{}"))

    return {"total": len(apps), "applications": apps}


@router.get("/{application_id}")
async def get_application(application_id: int):
    """Get a single application with full details including field logs."""
    app = await fetch_one(
        """SELECT a.*,
                  o.name as opportunity_name,
                  o.apply_url as opportunity_apply_url,
                  m.score as match_score,
                  m.reasoning as match_reasoning
           FROM applications a
           JOIN matches m ON a.match_id = m.id
           JOIN opportunities o ON m.opportunity_id = o.id
           WHERE a.id = ?""",
        (application_id,),
    )

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app["form_data"] = json.loads(app.get("form_data", "{}"))

    # Get field logs
    field_logs = await fetch_all(
        "SELECT * FROM field_logs WHERE application_id = ? ORDER BY created_at",
        (application_id,),
    )
    app["field_logs"] = field_logs

    return app


@router.post("/fill")
async def fill_form(request: FillRequest):
    """Trigger the form-fill agent for an opportunity. Does NOT submit."""
    def _sync_runner():
        import asyncio
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                fill_application(
                    opportunity_id=request.opportunity_id,
                    profile_id=request.profile_id,
                )
            )
        finally:
            loop.close()

    import asyncio
    result = await asyncio.to_thread(_sync_runner)
    return result


@router.get("/{application_id}/screenshot")
async def get_screenshot(application_id: int):
    """Get the screenshot of the filled form."""
    app = await fetch_one(
        "SELECT screenshot_path FROM applications WHERE id = ?",
        (application_id,),
    )
    if not app or not app.get("screenshot_path"):
        raise HTTPException(status_code=404, detail="Screenshot not found")

    screenshot_path = Path(app["screenshot_path"])
    if not screenshot_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot file not found")

    return FileResponse(
        str(screenshot_path),
        media_type="image/png",
        filename=screenshot_path.name,
        content_disposition_type="inline"
    )


@router.post("/{application_id}/approve")
async def approve_application(application_id: int, request: ApprovalRequest):
    """
    Approve or reject a filled application.

    If approved, the form will be submitted.
    If rejected, status changes to 'rejected'.
    """
    app = await fetch_one(
        "SELECT * FROM applications WHERE id = ?", (application_id,)
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app["status"] != "awaiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Application must be in 'awaiting_approval' status. Current: {app['status']}",
        )

    if not request.approved:
        await execute_update(
            "UPDATE applications SET status = 'rejected' WHERE id = ?",
            (application_id,),
        )
        return {"status": "rejected", "message": "Application rejected"}

    # Mark as approved
    await execute_update(
        "UPDATE applications SET status = 'approved', approved_at = datetime('now') WHERE id = ?",
        (application_id,),
    )

    # Submit the application
    result = await submit_application(application_id)
    return result


@router.get("/{application_id}/field-logs")
async def get_field_logs(application_id: int):
    """Get the field-by-field fill log for debugging."""
    logs = await fetch_all(
        "SELECT * FROM field_logs WHERE application_id = ? ORDER BY created_at",
        (application_id,),
    )
    return {"total": len(logs), "field_logs": logs}
