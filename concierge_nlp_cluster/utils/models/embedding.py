# concierge-nlp-cluster/concierge_nlp_cluster/utils/embedding.py

import openai
import numpy as np
import warnings
from . import embedding_model, max_tokens


def get_embedding(text, api_key, model=embedding_model):
    openai.api_key = api_key
    try:
        if text is None or len(text) == 0:
            return None

        input_list = [text]
        response = openai.Embedding.create(input=input_list, model=model)
        return np.array(response["data"][0]["embedding"])
    except Exception as e:
        warnings.warn(f"Embedding failed for text: {text}. Error: {str(e)}")
        return None
