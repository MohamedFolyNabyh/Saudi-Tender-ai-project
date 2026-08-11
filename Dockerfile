FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first
COPY requirements.txt .

# Install CPU-only PyTorch first
RUN python -m pip install --upgrade pip \
    && python -m pip install \
        torch==2.8.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r requirements.txt

# Application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]