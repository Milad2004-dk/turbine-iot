# Tag Python som udgangspunkt
FROM python:3.11-slim

# Sæt arbejdsmappen inde i containeren
WORKDIR /app

# Kopier requirements og installer libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopier resten af koden
COPY TurbineApi.py .

# Åbn port 5001
EXPOSE 5001

# Start API'et
CMD ["python", "TurbineApi.py"]
