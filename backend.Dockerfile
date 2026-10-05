FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc g++ make git libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and modules
COPY backend/requirements.txt backend/
COPY static-analysis/ static-analysis/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir joblib scikit-learn lightgbm pandas "bcrypt<4.0.0"
RUN pip install --no-cache-dir -e static-analysis/

COPY backend/ backend/
COPY models/ models/

WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
