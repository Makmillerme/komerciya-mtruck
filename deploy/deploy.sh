#!/bin/bash
# Скрипт деплою генератора комерційних пропозицій на сервер (on-demand режим)
# Використання: ./deploy.sh (запускати з папки komerciya_mtruck на сервері)

set -e

# APP_DIR — каталог проекту (батьківський до deploy/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${APP_DIR}/venv"

echo "=== Деплой komerciya-mtruck ==="

# Перевірка наявності Python 3
if ! command -v python3 &> /dev/null; then
    echo "Помилка: Python 3 не знайдено. Встановіть: apt install python3 python3-venv python3-pip"
    exit 1
fi

# Визначення режиму: on-demand (systemd >= 246) або простий (постійний)
USE_ONDEMAND=false
if command -v systemd-socket-proxyd &> /dev/null; then
    USE_ONDEMAND=true
    echo "Режим: on-demand (systemd-socket-proxyd знайдено)"
else
    echo "Режим: простий (постійний) — systemd-socket-proxyd не знайдено"
fi

# Створення venv якщо не існує
if [ ! -d "${VENV_DIR}" ]; then
    echo "Створення віртуального середовища..."
    python3 -m venv "${VENV_DIR}"
fi

# Активація venv та встановлення залежностей
echo "Встановлення залежностей..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r "${APP_DIR}/requirements.txt"

# Встановлення браузерів Playwright
echo "Встановлення Playwright Chromium..."
playwright install chromium
playwright install-deps chromium 2>/dev/null || true

# Створення папок uploads та output
mkdir -p "${APP_DIR}/uploads" "${APP_DIR}/output"

# Копіювання systemd unit-файлів
systemctl daemon-reload

if [ "$USE_ONDEMAND" = true ]; then
    sed "s|__APP_DIR__|${APP_DIR}|g" "${APP_DIR}/deploy/komerciya-mtruck-app.service" > /tmp/komerciya-mtruck-app.service
    cp "${APP_DIR}/deploy/komerciya-mtruck.socket" /etc/systemd/system/komerciya_mtruck.socket
    cp "${APP_DIR}/deploy/komerciya-mtruck.service" /etc/systemd/system/komerciya_mtruck.service
    cp /tmp/komerciya-mtruck-app.service /etc/systemd/system/komerciya_mtruck_app.service
    systemctl daemon-reload
    systemctl enable komerciya_mtruck.socket
    systemctl start komerciya_mtruck.socket
    systemctl stop komerciya_mtruck.service 2>/dev/null || true
    systemctl stop komerciya_mtruck_app.service 2>/dev/null || true
    echo "Режим: on-demand — сервіс стартує при переході по посиланню, зупиняється через 5 хв"
else
    systemctl stop komerciya_mtruck.socket 2>/dev/null || true
    systemctl disable komerciya_mtruck.socket 2>/dev/null || true
    sed "s|__APP_DIR__|${APP_DIR}|g" "${APP_DIR}/deploy/komerciya-mtruck-simple.service" > /etc/systemd/system/komerciya_mtruck.service
    systemctl daemon-reload
    systemctl enable komerciya_mtruck.service
    systemctl restart komerciya_mtruck.service
    echo "Режим: простий — сервіс працює постійно"
fi

echo "=== Деплой завершено ==="
echo "URL: http://91.239.232.91:5000"
echo "Статус: systemctl status komerciya_mtruck"
