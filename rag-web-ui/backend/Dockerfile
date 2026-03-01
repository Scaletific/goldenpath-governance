FROM python:3.12-slim

WORKDIR /app

# Install backend dependencies
COPY rag-web-ui/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install RAG pipeline dependencies
COPY requirements.txt /app/rag-requirements.txt
RUN pip install --no-cache-dir -r /app/rag-requirements.txt 2>/dev/null || true

# Copy backend app
COPY rag-web-ui/backend/app.py /app/app.py

# Copy RAG pipeline (read-only at runtime via volume, but include for standalone)
COPY scripts/rag /app/scripts/rag
COPY schemas /app/schemas

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
