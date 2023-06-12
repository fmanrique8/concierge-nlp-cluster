# concierge-nlp-cluster/Dockerfile
FROM python:3.10

WORKDIR /concierge_nlp_cluster

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry export -f requirements.txt --output requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY concierge_nlp_cluster concierge_nlp_cluster
COPY config.yml config.yml
COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "concierge_nlp_cluster.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
