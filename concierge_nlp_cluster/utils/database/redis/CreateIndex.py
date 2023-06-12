# concierge-nlp-cluster/concierge_nlp_cluster/CreateIndex.py
import redis
import logging

from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TextField, NumericField

from concierge_nlp_cluster.utils.database.redis import (
    VECTOR_DIM,
    DISTANCE_METRIC,
)


class CreateIndex:
    def __init__(self, redis_conn: redis.Redis, index_name: str, prefix: str):
        self.redis_conn = redis_conn
        self.index_name = index_name
        self.prefix = prefix

    def __call__(self):
        document_name = TextField(name="document_name")
        text_chunks = TextField(name="text_chunks")
        vector_score = NumericField(name="vector_score")
        embedding = VectorField(
            "text_embeddings",
            "FLAT",
            {
                "TYPE": "FLOAT64",
                "DIM": VECTOR_DIM,
                "DISTANCE_METRIC": DISTANCE_METRIC,
                "INITIAL_CAP": 255,
            },
        )

        try:
            self.redis_conn.ft(self.index_name).create_index(
                fields=[
                    document_name,
                    text_chunks,
                    embedding,
                    vector_score,
                ],
                definition=IndexDefinition(
                    prefix=[self.prefix], index_type=IndexType.HASH
                ),
            )
        except redis.exceptions.ResponseError as e:
            if "Index already exists" in str(e):
                logging.warning(f"Index {self.index_name} already exists.")
            else:
                raise e
