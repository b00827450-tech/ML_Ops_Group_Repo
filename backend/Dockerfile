FROM python:3.11-slim AS builder

ENV POETRY_NO_INTERACTION=1

WORKDIR /build

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root \
    && cp -a "$(poetry env info --path)" /opt/venv

FROM python:3.11-slim

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY backend/ /app/

EXPOSE 8000

CMD ["python", "run.py"]
