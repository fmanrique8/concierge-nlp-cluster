# concierge-nlp-cluster/concierge_nlp_cluster/database.py
import logging
import redis
import pandas as pd

from redis.commands.search.query import Query
from concierge_nlp_cluster.utils.database.redis import NUM_VECTORS

# Logging set up
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_doc(doc: dict) -> dict:
    """
    Process document to handle vector_score and bytes data.

    Args:
    doc: dict: Document to be processed.

    Returns:
    dict: Processed document.
    """
    d = doc.__dict__
    if "vector_score" in d:
        d["vector_score"] = 1 - float(d["vector_score"])

    if isinstance(d["document_name"], bytes):
        d["document_name"] = d["document_name"].decode("utf-8", errors="ignore")
    if isinstance(d["text_chunks"], bytes):
        d["text_chunks"] = d["text_chunks"].decode("utf-8", errors="ignore")

    return d


def index_documents(redis_conn: redis.Redis, df: pd.DataFrame, prefix: str):
    """
    Index documents in Redis.

    Args:
    redis_conn: redis.Redis: Redis connection.
    df: pd.DataFrame: DataFrame containing documents to be indexed.
    prefix: str: Prefix to be used for document keys.

    """
    pipe = redis_conn.pipeline()
    for index, row in df.iterrows():
        key = f"{prefix}:{row['vector_id']}"
        document_data = {
            "document_name": row["document_name"],
            "text_chunks": row["text_chunks"],
            "text_embeddings": row["text_embeddings"].tobytes(),
        }
        pipe.hset(key, mapping=document_data)
        logger.info(f"Indexing document: {key}, document_data: {document_data}")
    pipe.execute()


def load_documents(redis_conn: redis.Redis, df: pd.DataFrame, prefix: str):
    """
    Load documents into Redis.

    Args:
    redis_conn: redis.Redis: Redis connection.
    df: pd.DataFrame: DataFrame containing documents to be loaded.
    prefix: str: Prefix to be used for document keys.

    """
    logger.info(f"Indexing {len(df)} Documents")
    index_documents(redis_conn, df, prefix)
    logger.info("Redis Vector Index Created!")


def list_docs(
    redis_conn: redis.Redis,
    index_name: str,
    k: int = NUM_VECTORS,
) -> list[dict]:
    """
    List documents from Redis index.

    Args:
    redis_conn: redis.Redis: Redis connection.
    index_name: str: Name of the index to fetch documents from.
    k: int: Maximum number of documents to fetch.

    Returns:
    list[dict]: List of documents from Redis index.

    """
    base_query = "*"
    return_fields = ["document_name", "text_chunks"]
    query = Query(base_query).paging(0, k).return_fields(*return_fields).dialect(2)
    results = redis_conn.ft(index_name).search(query)
    return [process_doc(doc) for doc in results.docs]


def delete_index(redis_conn: redis.Redis, index_name: str):
    """
    Delete a specific index from Redis.

    Args:
    redis_conn: redis.Redis: Redis connection.
    index_name: str: Name of the index to be deleted.

    """
    try:
        redis_conn.execute_command("FT.DROPINDEX", index_name)
        logger.info(f"Index {index_name} has been deleted.")
    except redis.exceptions.ResponseError as e:
        if "Unknown index name" in str(e):
            logger.info(f"Index {index_name} does not exist.")
        else:
            raise e


def clear_cache(redis_conn: redis.Redis):
    """
    Clear cache in Redis.

    Args:
    redis_conn: redis.Redis: Redis connection.

    """
    redis_conn.flushdb()
    logger.info("Cache cleared")
