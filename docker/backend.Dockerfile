FROM python:3.12-slim AS runtime-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY docker/scripts/start-backend.sh /usr/local/bin/start-backend
RUN chmod +x /usr/local/bin/start-backend

FROM runtime-base AS django-base
COPY docker/requirements/backend-common.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

FROM django-base AS mysql-base
COPY docker/requirements/backend-mysql.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

FROM django-base AS postgres-base
COPY docker/requirements/backend-postgres.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

FROM postgres-base AS ai-base
COPY docker/requirements/backend-ai.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

FROM django-base AS api_gateway
COPY common /app/common
COPY api_gateway /app
EXPOSE 8000
ENV DJANGO_WSGI=gateway.wsgi:application
ENV PORT=8000
CMD ["start-backend"]

FROM mysql-base AS user_service
COPY common /app/common
COPY user_service /app
EXPOSE 8001
ENV DJANGO_WSGI=user_service.wsgi:application
ENV PORT=8001
CMD ["start-backend"]

FROM mysql-base AS staff_service
COPY common /app/common
COPY staff_service /app
EXPOSE 8002
ENV DJANGO_WSGI=staff_service.wsgi:application
ENV PORT=8002
CMD ["start-backend"]

FROM postgres-base AS product_service
COPY common /app/common
COPY product_service /app
EXPOSE 8003
ENV DJANGO_WSGI=product_service.wsgi:application
ENV PORT=8003
CMD ["start-backend"]

FROM postgres-base AS cart_service
COPY common /app/common
COPY cart_service /app
EXPOSE 8004
ENV DJANGO_WSGI=cart_service.wsgi:application
ENV PORT=8004
CMD ["start-backend"]

FROM postgres-base AS order_service
COPY common /app/common
COPY order_service /app
EXPOSE 8005
ENV DJANGO_WSGI=order_service.wsgi:application
ENV PORT=8005
CMD ["start-backend"]

FROM mysql-base AS payment_service
COPY common /app/common
COPY payment_service /app
EXPOSE 8006
ENV DJANGO_WSGI=payment_service.wsgi:application
ENV PORT=8006
CMD ["start-backend"]

FROM mysql-base AS shipping_service
COPY common /app/common
COPY shipping_service /app
EXPOSE 8007
ENV DJANGO_WSGI=shipping_service.wsgi:application
ENV PORT=8007
CMD ["start-backend"]

FROM postgres-base AS comment_service
COPY common /app/common
COPY comment_service /app
EXPOSE 8008
ENV DJANGO_WSGI=comment_service.wsgi:application
ENV PORT=8008
CMD ["start-backend"]

FROM ai-base AS ai_service
COPY common /app/common
COPY ai_service /app
EXPOSE 8009
ENV DJANGO_WSGI=ai_service.wsgi:application
ENV PORT=8009
CMD ["start-backend"]
