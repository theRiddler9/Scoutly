"""
Scoutly — Pydantic Models (Request / Response Schemas)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ── Profile ────────────────────────────────────────────────────────────────────

class ProjectItem(BaseModel):
    title: str = ""
    description: str = ""
    tech_stack: str = ""


class SocialHandles(BaseModel):
    twitter: str = ""
    linkedin: str = ""
    website: str = ""


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=1)
    github_url: str = ""
    skills: list[str] = []
    projects: list[ProjectItem] = []
    resume_text: str = ""
    social_handles: SocialHandles = SocialHandles()


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    github_url: Optional[str] = None
    skills: Optional[list[str]] = None
    projects: Optional[list[ProjectItem]] = None
    resume_text: Optional[str] = None
    social_handles: Optional[SocialHandles] = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    github_url: str
    skills: list[str]
    projects: list[ProjectItem]
    resume_text: str
    social_handles: SocialHandles
    created_at: str
    updated_at: str


# ── Opportunity ────────────────────────────────────────────────────────────────

class OpportunityResponse(BaseModel):
    id: int
    name: str
    source_url: str
    apply_url: str
    deadline: str
    eligibility_summary: str
    prize_info: str
    description: str
    organizer: str
    tags: list[str]
    status: str
    discovered_at: str
    # Match data (optional, when joined)
    match_score: Optional[int] = None
    match_reasoning: Optional[str] = None
    qualifies: Optional[bool] = None
    deadline_feasible: Optional[bool] = None


class OpportunityListResponse(BaseModel):
    total: int
    opportunities: list[OpportunityResponse]


# ── Match ──────────────────────────────────────────────────────────────────────

class MatchResponse(BaseModel):
    id: int
    profile_id: int
    opportunity_id: int
    qualifies: bool
    score: int
    reasoning: str
    deadline_feasible: bool
    matched_at: str


class MatchTriggerRequest(BaseModel):
    profile_id: int = 1
    opportunity_ids: Optional[list[int]] = None  # None = match all unmatched


# ── Application ────────────────────────────────────────────────────────────────

class ApplicationResponse(BaseModel):
    id: int
    match_id: int
    status: str
    form_data: dict
    screenshot_path: str
    error_message: str
    filled_at: Optional[str] = None
    approved_at: Optional[str] = None
    submitted_at: Optional[str] = None
    created_at: str
    # Joined data
    opportunity_name: Optional[str] = None
    opportunity_apply_url: Optional[str] = None
    match_score: Optional[int] = None


class ApplicationListResponse(BaseModel):
    total: int
    applications: list[ApplicationResponse]


class FillRequest(BaseModel):
    opportunity_id: int
    profile_id: int = 1


class ApprovalRequest(BaseModel):
    approved: bool = True


# ── Field Log ──────────────────────────────────────────────────────────────────

class FieldLogResponse(BaseModel):
    id: int
    application_id: int
    field_label: str
    field_type: str
    filled_value: str
    reasoning: str
    created_at: str


# ── Discovery ─────────────────────────────────────────────────────────────────

class DiscoverySource(BaseModel):
    name: str
    url: str
    type: str


class DiscoveryRunRequest(BaseModel):
    source_urls: Optional[list[DiscoverySource]] = None  # None = use defaults


class DiscoveryRunResponse(BaseModel):
    status: str
    new_opportunities: int
    total_scraped: int
    errors: list[str]


# ── Dashboard Stats ───────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_opportunities: int
    matched_opportunities: int
    pending_approvals: int
    submitted_applications: int
    avg_match_score: float
    upcoming_deadlines: list[dict]
