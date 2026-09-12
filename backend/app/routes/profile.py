"""
Scoutly — Profile Routes
"""

import json
from fastapi import APIRouter, HTTPException
from app.models import ProfileCreate, ProfileUpdate, ProfileResponse
from app.database import fetch_one, fetch_all, execute_insert, execute_update

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.post("", response_model=dict)
async def create_profile(profile: ProfileCreate):
    """Create a new user profile."""
    row_id = await execute_insert(
        """INSERT INTO profiles (name, email, github_url, skills, projects, resume_text, social_handles)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            profile.name,
            profile.email,
            profile.github_url,
            json.dumps(profile.skills),
            json.dumps([p.model_dump() for p in profile.projects]),
            profile.resume_text,
            json.dumps(profile.social_handles.model_dump()),
        ),
    )
    return {"id": row_id, "message": "Profile created successfully"}


@router.get("/{profile_id}")
async def get_profile(profile_id: int):
    """Get a user profile by ID."""
    profile = await fetch_one("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Parse JSON fields
    profile["skills"] = json.loads(profile.get("skills", "[]"))
    profile["projects"] = json.loads(profile.get("projects", "[]"))
    profile["social_handles"] = json.loads(profile.get("social_handles", "{}"))
    return profile


@router.get("")
async def list_profiles():
    """List all profiles."""
    profiles = await fetch_all("SELECT * FROM profiles ORDER BY created_at DESC")
    for p in profiles:
        p["skills"] = json.loads(p.get("skills", "[]"))
        p["projects"] = json.loads(p.get("projects", "[]"))
        p["social_handles"] = json.loads(p.get("social_handles", "{}"))
    return {"profiles": profiles}


@router.put("/{profile_id}")
async def update_profile(profile_id: int, profile: ProfileUpdate):
    """Update an existing profile."""
    existing = await fetch_one("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found")

    updates = {}
    if profile.name is not None:
        updates["name"] = profile.name
    if profile.email is not None:
        updates["email"] = profile.email
    if profile.github_url is not None:
        updates["github_url"] = profile.github_url
    if profile.skills is not None:
        updates["skills"] = json.dumps(profile.skills)
    if profile.projects is not None:
        updates["projects"] = json.dumps([p.model_dump() for p in profile.projects])
    if profile.resume_text is not None:
        updates["resume_text"] = profile.resume_text
    if profile.social_handles is not None:
        updates["social_handles"] = json.dumps(profile.social_handles.model_dump())

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [profile_id]
        await execute_update(
            f"UPDATE profiles SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
            tuple(values),
        )

    return {"message": "Profile updated successfully"}


@router.delete("/{profile_id}")
async def delete_profile(profile_id: int):
    """Delete a profile."""
    rows = await execute_update("DELETE FROM profiles WHERE id = ?", (profile_id,))
    if rows == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}
