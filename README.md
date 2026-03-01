Контейнеризация Django-приложения (Docker + PostgreSQL + Nginx)

## Описание

Проект представляет собой Django‑приложение из лабораторной работы №5, упакованное в контейнеры Docker и развёрнутое на виртуальной машине Kali Linux.  
Используются следующие компоненты:

- Django + Gunicorn (сервис `web`)
- PostgreSQL (сервис `db`)
- Nginx (reverse proxy, сервис `nginx`)
- Docker Compose для оркестрации

## Предварительные требования

- Виртуальная машина с **Kali Linux**
- Установленные **Docker** и **Docker Compose Plugin**

Проверка установки:

```bash
docker --version
docker compose version
При необходимости установка (Kali):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# затем перелогиниться
Проект размещается в директории:

```bash
/var/www/web_2025
Структура проекта
- Ключевые файлы и директории:

docker-compose.yml — описание сервисов db, web, nginx

.env — переменные окружения для Django и PostgreSQL

django/Dockerfile — образ приложения (Django + Gunicorn)

django/entrypoint.sh — запуск миграций и Gunicorn

django/requirements.base.txt, django/requirements.prod.txt — зависимости

nginx/Dockerfile — образ Nginx

nginx/nginx.conf — конфигурация Nginx (проксирование запросов и статика)

исходный код Django‑проекта (каталог с manage.py и модулем настроек)

Конфигурация окружения
В корне проекта должен находиться файл .env. Пример:

```text
DJANGO_SECRET_KEY=замени_на_секрет
DJANGO_DEBUG=False

DB_NAME=fefu_lab_db
DB_USER=fefu_user
DB_PASSWORD=сильный_пароль
DB_HOST=db
DB_PORT=5432
Django использует эти переменные для настройки SECRET_KEY, режима DEBUG и параметров подключения к базе данных.

Сборка контейнеров
Все команды выполняются в директории проекта:

```bash
cd /var/www/web_2025
docker compose build
Команда собирает:

образ приложения (web) из django/Dockerfile;

образ веб‑сервера (nginx) из nginx/Dockerfile;

использует официальный образ postgres:15-alpine для сервиса db.

Запуск приложения
Запуск в фоновом режиме:

```bash
cd /var/www/web_2025
docker compose up -d
Проверка статуса контейнеров:

```bash
docker compose ps
Ожидаемые сервисы:

web_2025_db — PostgreSQL, состояние running (healthy)

web_2025_web — Django + Gunicorn, состояние running

web_2025_nginx — Nginx, проброшен на порт 80 хостовой системы

Поведение при старте
При запуске контейнера web выполняется скрипт django/entrypoint.sh:

```bash
#!/usr/bin/env bash
set -e

echo "Run migrations..."
python manage.py migrate --noinput

exec "$@"
выполняются миграции Django;

далее запускается Gunicorn (как указано в CMD Dockerfile).

Статические файлы собираются на этапе сборки образа командой:

```bash
python manage.py collectstatic --noinput
Nginx раздаёт статику и проксирует запросы на Gunicorn (сервис web) согласно nginx/nginx.conf.

Доступ к приложению
На Kali Linux (внутри VM)
```bash
curl http://localhost
Должен вернуться HTML‑ответ Django‑приложения.

С хостовой машины
Узнать IP‑адрес VM (на Kali):

```bash
ip a
Открыть в браузере на хосте:

```text
http://<IP_КАЛИ>/
Ожидается отображение веб‑интерфейса приложения, развёрнутого в контейнерах.

Остановка и перезапуск
Остановка и удаление контейнеров:

```bash
cd /var/www/web_2025
docker compose down
Пересборка и повторный запуск (после изменений в коде или конфигурации):

```bash
docker compose build
docker compose up -d
Диагностика
Просмотр логов всех сервисов:

```bash
docker compose logs
Отдельно приложение:

```bash
docker compose logs web
Отдельно Nginx:

```bash
docker compose logs nginx
Отдельно базу данных:

```bash
docker compose logs db

Выключение приложения
```bash
docker compose down