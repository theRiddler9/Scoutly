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

    def _sync_runner(srcs):
        import asyncio
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_discovery(source_urls=srcs))
        finally:
            loop.close()

    import asyncio
    result = await asyncio.to_thread(_sync_runner, sources)
    return result


@router.get("/sources")
async def list_sources():
    """List the configured discovery source URLs."""
    return {"sources": DEFAULT_SOURCE_URLS}
