FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy Python files
COPY worker.py /app/
COPY query_engine_client.py /app/

CMD ["python", "/app/worker.py"]