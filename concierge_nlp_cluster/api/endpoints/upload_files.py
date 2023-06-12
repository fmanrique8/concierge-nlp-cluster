import logging
from fastapi import File, UploadFile, APIRouter
from typing import List
from datetime import datetime

from concierge_nlp_cluster import API_KEY, redis_conn
from concierge_nlp_cluster.utils.database.redis.database import (
    load_documents,
    delete_index,
    clear_cache,
)
from concierge_nlp_cluster.utils.database.redis.CreateIndex import CreateIndex
from concierge_nlp_cluster.utils.preprocess.preprocess import (
    intermediate_processor,
    primary_processor,
)

# Creating an API router
router = APIRouter()

# Logging set up
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_exists(index_name: str) -> bool:
    """
    Function to check if index exists.

    Args:
    index_name: str: The index name to check

    Returns:
    bool: Whether the index exists or not.
    """
    indices = redis_conn.execute_command("FT._LIST")
    return index_name in indices


@router.post("/")
async def upload_files_endpoint(
    client_id: str, files: List[UploadFile] = File(...)
) -> dict:
    """
    Endpoint to upload files.

    Args:
    client_id: str: ID of the client.
    files: List of files to be uploaded.

    Returns:
    dict: A dictionary containing status and message.
    """
    # Set the index_name using the client's ID
    index_name = f"concierge-db-index-{client_id}"
    prefix = "document"

    # Read the contents of the files and store them in a list
    file_contents = []
    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    # Process the file contents using intermediate and primary processors
    df = intermediate_processor(file_contents)
    df = primary_processor(df, API_KEY)

    # Check if index already exists, if yes delete it
    if index_exists(index_name):
        delete_result = delete_index(redis_conn, index_name)
        if delete_result["status"] == "warning":
            logger.warning(delete_result["message"])

    # Create index in Redis and load documents into the index
    indexer = CreateIndex(redis_conn, index_name, prefix)
    indexer()
    load_documents(redis_conn, df, prefix)

    logger.info(f"Files uploaded and stored in Redis with index: {index_name}")

    return {
        "status": "success",
        "message": "Files uploaded and stored in Redis",
        "index_name": index_name,
    }
