FROM python:3.11-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cracked_rotor ./cracked_rotor
COPY main.py app.py ./

ENV OUTPUT_DIR=/app/output
ENV PORT=10000
EXPOSE 10000

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}
