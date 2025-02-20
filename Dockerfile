FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && apt-get install procps -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ph-sync.py .
COPY app/start.sh .

RUN chmod +x start.sh

RUN pip install requests

CMD ["/app/start.sh"]