# Dockerfile for AsciiDoc Linter
FROM python:3.9-slim

LABEL org.opencontainers.image.source="https://github.com/docToolchain/asciidoc-linter"
LABEL org.opencontainers.image.description="A linter for AsciiDoc files"
LABEL org.opencontainers.image.licenses="MIT"

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY pyproject.toml setup.py ./
COPY asciidoc_linter/ ./asciidoc_linter/

# Install the project
RUN pip install --no-cache-dir .

# Set working directory for linting
WORKDIR /docs

# Set the entry point to the linter CLI
ENTRYPOINT ["asciidoc-linter"]
