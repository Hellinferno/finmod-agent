FROM python:3.11-slim

WORKDIR /app

# Dependencies
# Install system dependencies for Kaleido/Export
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source Code
COPY src/ /app/src/

# Environment
ENV PYTHONPATH=/app

# Port
EXPOSE 8050

# Command
CMD ["python", "src/ui/app.py"]
