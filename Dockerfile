# Multi-stage Docker build for HandBrake MCP Server
FROM python:3.13-slim as builder

# Set build arguments
ARG VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    DEBIAN_FRONTEND=noninteractive

# Set labels
LABEL org.opencontainers.image.title="HandBrake MCP Server" \
      org.opencontainers.image.description="MCP server for HandBrake video transcoding" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.vendor="Sandra Schi" \
      org.opencontainers.image.source="https://github.com/sandraschi/handbrake-mcp" \
      org.opencontainers.image.licenses="MIT"

# Install HandBrake CLI from Debian repos
RUN apt-get update && apt-get install -y handbrake-cli && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY .env.example ./

# Install Python dependencies (fleet standard: uv)
RUN pip install uv && uv sync --no-dev --no-install-project

# Copy source code
COPY src/ ./src/

# Finish install with source
RUN uv sync --no-dev

# Create non-root user
RUN useradd --create-home --shell /bin/bash handbrake && \
    chown -R handbrake:handbrake /app

# Switch to non-root user
USER handbrake

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import handbrake_mcp; print('Service is running')" || exit 1

# Expose port
EXPOSE 8000

# Set default command
CMD ["uv", "run", "python", "-m", "uvicorn", "handbrake_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Production image
FROM python:3.13-slim as production

# Install runtime dependencies (handbrake-cli from Debian repos)
RUN apt-get update && apt-get install -y \
    handbrake-cli \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary for production CMD
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY --from=builder /app /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash handbrake && \
    chown -R handbrake:handbrake /app

# Switch to non-root user
USER handbrake

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import handbrake_mcp; print('Service is running')" || exit 1

# Expose port
EXPOSE 8000

# Set default command
CMD ["uv", "run", "python", "-m", "uvicorn", "handbrake_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development image
FROM builder as development

# Install development dependencies
RUN uv sync --group dev

# Set development environment
ENV ENVIRONMENT=development \
    LOG_LEVEL=debug

# Override command for development
CMD ["uv", "run", "python", "-m", "uvicorn", "handbrake_mcp.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
