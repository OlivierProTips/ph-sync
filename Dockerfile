FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ .
COPY requirements.txt .

RUN chmod +x start.sh

RUN pip install -r requirements.txt

CMD ["/app/start.sh"]
