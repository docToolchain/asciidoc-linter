# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY . /app

# Install the project dependencies
RUN pip install --no-cache-dir -e .
RUN pip install pyyaml

# Set the entry point to the linter CLI
ENTRYPOINT ["asciidoc-lint"]
