FROM python:3.11-slim

# Install system dependencies for aerospace math (gfortran for some HPOP libs)
RUN apt-get update && apt-get install -y gfortran liblapack-dev libblas-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Run with Gunicorn + Uvicorn for production-grade concurrency
CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
