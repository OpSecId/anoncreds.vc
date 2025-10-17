FROM python:3.12

WORKDIR /flask

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

COPY app ./app
COPY config.py main.py ./

# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
CMD ["uv", "run", "python", "main.py"]