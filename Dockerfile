# Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates iptables \
    && curl -fsSL https://tailscale.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY deploy/start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

RUN adduser --disabled-password --gecos "" appuser

CMD ["/app/start.sh"]
