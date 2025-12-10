# Use the official uv image with preinstalled Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# uv and Python settings
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 1. Copy dependency files first (to leverage Docker layer caching)
COPY pyproject.toml uv.lock ./

# 2. Install dependencies (without the project itself and without dev packages)
# --frozen: strictly follow uv.lock
# --no-install-project: do not install the project yet
# --no-dev: skip dev dependencies like pytest, ruff, etc.
RUN uv sync --frozen --no-install-project --no-dev

# 3. Copy source code
COPY src ./src
COPY data ./data
# README is needed only if it is used in setup; otherwise may be skipped
COPY README.md .

# 4. Install the project itself
RUN uv sync --frozen --no-dev

# 5. Add the virtual environment to PATH
# Now 'python' will refer to the Python inside .venv
ENV PATH="/app/.venv/bin:$PATH"

# Run the application in daemon loop mode
# Interval can be overridden via ENV or docker-compose command
CMD ["python", "-m", "src.content_agents.main", "--loop", "--interval", "3600"]
