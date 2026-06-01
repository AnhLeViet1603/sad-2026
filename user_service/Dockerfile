FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential pkg-config && rm -rf /var/lib/apt/lists/*
COPY user_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY common /app/common
COPY user_service /app

EXPOSE 8001
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn user_service.wsgi:application --bind 0.0.0.0:8001"]

