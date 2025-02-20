FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ .
COPY requirements.txt .

RUN chmod +x start.sh

RUN pip install -r requirements.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f cron || exit 1

CMD ["/app/start.sh"]
