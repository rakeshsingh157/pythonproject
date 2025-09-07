# Base image
FROM python:3.10.11-slim

# Working directory
WORKDIR /app

COPY requirements.txt .
RUN pip --default-timeout=100 install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Expose FastAPI port
EXPOSE 5000

# Run FastAPI
CMD ["uvicorn", "send_email_api:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
