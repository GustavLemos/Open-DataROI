FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py"]

# roi_estimator/docker-compose.yml
version: '3.8'
services:
  roi-estimator:
    build: .
    ports:
      - "8501:8501"  # Streamlit
      - "8000:8000"  # FastAPI
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
