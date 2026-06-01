FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY api_gateway/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY common /app/common
COPY api_gateway /app

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn gateway.wsgi:application --bind 0.0.0.0:8000"]

