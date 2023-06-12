# romeo-gtp/concierge_nlp_cluster/api/__init__.py
from fastapi import APIRouter, Depends
from .endpoints.upload_files import router as upload_files_router

router = APIRouter()

# Include the upload_files_router with prefix, tags, and rate limiting
router.include_router(
    upload_files_router,
    prefix="/upload-files",
    tags=["upload-files"],
)
