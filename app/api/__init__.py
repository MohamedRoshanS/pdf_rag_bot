from fastapi import APIRouter

# Router aggregator so you can include a single router in app.main if preferred.
# main.py currently mounts documents & query directly, but this keeps options open.

router = APIRouter()

try:
    from .documents import router as documents_router
    from .query import router as query_router
    router.include_router(documents_router, prefix="", tags=["documents"])
    router.include_router(query_router, prefix="", tags=["query"])
except Exception:
    # If modules aren't importable during certain tooling phases, skip aggregation.
    # main.py already imports the routers directly, so runtime is unaffected.
    pass

__all__ = ["router"]
