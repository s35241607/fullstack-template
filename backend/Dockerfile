FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen

# Copy source (overridden by volume mount in docker-compose dev mode)
COPY . .

EXPOSE 8000 5678
