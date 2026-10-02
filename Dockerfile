FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md COPYRIGHT.md ./
COPY src ./src

RUN python -m pip install --upgrade pip && \
    pip install .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn sitepulse.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
