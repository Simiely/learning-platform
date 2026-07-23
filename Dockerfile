FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Safe default; docker-compose overrides DJANGO_DEBUG=True so media/static are served.
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=*

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic moved to entrypoint — needs SECRET_KEY / DEBUG at runtime
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
