FROM python:3.11-slim

RUN apt-get update && apt-get install -y poppler-utils

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
