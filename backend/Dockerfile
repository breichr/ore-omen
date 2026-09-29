# Build context: repository root (needs backend/ and content/), see docker-compose.yml
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir "uv>=0.8,<1"

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/ .
COPY content/ /app/content/
ENV PATH="/app/.venv/bin:$PATH" OO_CONTENT_DIR=/app/content

RUN useradd --system --uid 1000 app && chown -R app /app
USER app

EXPOSE 8000
# Migrations run on API start (docs/08-technik.md, "Deployment")
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
