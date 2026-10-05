FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security compliance
RUN groupadd -r botgroup && useradd -r -g botgroup -d ${APP_HOME} -s /sbin/nologin botuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY db ${APP_HOME}/db
COPY bot ${APP_HOME}/bot

RUN chown -R botuser:botgroup ${APP_HOME}

USER botuser

CMD ["python", "-m", "bot.main"]
