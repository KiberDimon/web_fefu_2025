#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/KiberDimon/web_fefu_2025"
APP_DIR="/var/www/web_2025"
VENV_DIR="$APP_DIR/venv"

echo "[1] Установка системных пакетов"
sudo apt update
sudo apt install -y python3-venv python3-pip git nginx postgresql postgresql-contrib

echo "[2] Подготовка каталога приложения"
sudo rm -rf "$APP_DIR"
sudo mkdir -p "$APP_DIR"
sudo chown "$USER:$USER" "$APP_DIR"

echo "[3] Клонирование репозитория"
git clone "$REPO_URL" "$APP_DIR"

cd "$APP_DIR"

echo "[4] Виртуальное окружение и зависимости"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "[5] Миграции и статика"
python manage.py migrate --run-syncdb
if [ -f "data.json" ]; then
  python manage.py loaddata data.json || true
fi
python manage.py collectstatic --noinput

echo "[6] Nginx"
sudo cp deploy/nginx/fefu_lab.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/fefu_lab.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "[7] Gunicorn"
sudo cp deploy/systemd/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

echo "[8] Проверка curl"
curl -I http://localhost:80 || echo "curl не смог достучаться до nginx"

echo "Готово"
