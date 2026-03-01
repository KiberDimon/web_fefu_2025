# ---------- build stage ----------
FROM python:3.11 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# requirements
COPY django/requirements.dev.txt django/requirements.prod.txt /tmp/
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.prod.txt

# копируем весь проект (manage.py, web_2025/ и т.д.)
COPY . /app

ENV DJANGO_SETTINGS_MODULE=web_2025.settings

# собираем статику (Django уже установлен в этом образе)
RUN python manage.py collectstatic --noinput

# ---------- production stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system django && adduser --system --ingroup django django

WORKDIR /app

# ставим зависимости ещё раз (в прод-образе)
COPY django/requirements.dev.txt django/requirements.prod.txt /tmp/
RUN apt-get update && apt-get install -y \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.prod.txt

# копируем код приложения
COPY . /app

# копируем статику из builder
COPY --from=builder /app/static /app/static

RUN chown -R django:django /app
USER django

COPY django/entrypoint.sh /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "web_2025.wsgi:application", "--bind", "0.0.0.0:8000"]

