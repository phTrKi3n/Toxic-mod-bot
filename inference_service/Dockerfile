FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for container security
RUN groupadd -r appgroup && useradd -r -g appgroup -d ${APP_HOME} -s /sbin/nologin appuser

# Copy dependency files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY db ${APP_HOME}/db
COPY inference_service ${APP_HOME}/inference_service

# Grant ownership to non-root appuser
RUN chown -R appuser:appgroup ${APP_HOME}

# Switch to non-root security context
USER appuser

EXPOSE 8000

CMD ["uvicorn", "inference_service.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
