FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev build-essential && rm -rf /var/lib/apt/lists/*
COPY ai_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY common /app/common
COPY ai_service /app

EXPOSE 8009
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn ai_service.wsgi:application --bind 0.0.0.0:8009"]

