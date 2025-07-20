FROM python:3.9-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir gunicorn==20.1.0 uvicorn==0.22.0 && \
    pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    ALEMBIC_CONFIG=/app/alembic.ini \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker app.main:app"]