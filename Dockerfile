FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV UV_LINK_MODE=copy OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY configs ./configs
COPY reports ./reports
RUN uv sync --locked --no-dev --python 3.11
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "retailmind.api:app", "--host", "0.0.0.0", "--port", "8000"]