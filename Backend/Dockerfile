# ---------- Build stage ----------
    FROM python:3.12-slim AS builder
    WORKDIR /app
    
    # Install system dependencies and Poetry
    RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
    RUN pip install poetry
    
    # Copy Poetry files and install dependencies
    COPY pyproject.toml poetry.lock ./
    RUN poetry config virtualenvs.create false \
     && poetry install --no-root
    
    # ---------- Final stage ----------
    FROM python:3.12-slim
    WORKDIR /app
    
    # Copy installed dependencies from builder
    COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
    COPY --from=builder /usr/local/bin/ /usr/local/bin/
    
    # Copy your app files
    COPY app.py chatbot.py ./
    
    # Copy the .env file if needed during build (for dev only; better to mount it or use docker-compose in prod)
    # COPY .env ./
    
    # Expose port
    EXPOSE 5000
    
    # Run init + Gunicorn as entrypoint
    CMD ["sh", "-c", "python -c 'import app' && gunicorn --bind 0.0.0.0:5000 --timeout 900 app:app"]
    