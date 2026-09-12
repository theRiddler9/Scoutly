"""
Scoutly — Discovery Routes
"""

from fastapi import APIRouter
from app.services.discovery import run_discovery
from app.config import DEFAULT_SOURCE_URLS
from app.models import DiscoveryRunRequest

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


@router.post("/run")
async def trigger_discovery(request: DiscoveryRunRequest = DiscoveryRunRequest()):
    """
    Trigger a discovery scan to find new opportunities.
    Optionally pass custom source URLs; defaults to configured sources.
    """
    sources = None
    if request.source_urls:
        sources = [s.model_dump() for s in request.source_urls]

    result = await run_discovery(source_urls=sources)
    return result


@router.get("/sources")
async def list_sources():
    """List the configured discovery source URLs."""
    return {"sources": DEFAULT_SOURCE_URLS}
