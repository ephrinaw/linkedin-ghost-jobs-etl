# LinkedIn Ghost Jobs ETL Pipeline - Production Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml .
COPY README.md .

# Create necessary directories
RUN mkdir -p data/{raw,transformed,outputs} logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash etl_user \
    && chown -R etl_user:etl_user /app
USER etl_user

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import src.config.settings; print('OK')" || exit 1

# Default command
CMD ["python", "src/main.py", "run_etl"]

# Labels for metadata
LABEL maintainer="your.email@example.com" \
      version="1.0.0" \
      description="LinkedIn Ghost Jobs ETL Pipeline" \
      org.opencontainers.image.source="https://github.com/yourusername/linkedin-ghost-jobs-etl"