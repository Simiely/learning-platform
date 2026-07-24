FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Safe default; docker-compose overrides DJANGO_DEBUG=True so media/static are served.
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=*

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 libglib2.0-0 libgomp1 rsync \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep bundled copy of media so entrypoint can sync updates to volume
RUN cp -r /app/media /app/media-bundled

# collectstatic moved to entrypoint — needs SECRET_KEY / DEBUG at runtime
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Run as non-root for security
RUN useradd -m app && chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
