FROM python:3.10-slim

WORKDIR /app

# Install YARA and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    libyara-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY installer/ ./installer/
COPY tests/ ./tests/
COPY render.yaml .
COPY vercel.json .

ENV PYTHONPATH=/app
ENV PORT=5000
ENV RENDER=true

EXPOSE 5000

CMD ["python", "-m", "src.web_server"]
