#!/bin/bash
# Скрипт деплою генератора комерційних пропозицій на сервер (on-demand режим)
# Використання: ./deploy.sh (запускати з папки komerciya_mtruck на сервері)

set -e

APP_NAME="komerciya_mtruck"
APPS_DIR="/root/apps"
APP_DIR="${APPS_DIR}/${APP_NAME}"
VENV_DIR="${APP_DIR}/venv"

echo "=== Деплой ${APP_NAME} (on-demand) ==="

# Перевірка наявності Python 3
if ! command -v python3 &> /dev/null; then
    echo "Помилка: Python 3 не знайдено. Встановіть: apt install python3 python3-venv python3-pip"
    exit 1
fi

# Перевірка systemd-socket-proxyd (потрібен systemd >= 246)
if ! command -v systemd-socket-proxyd &> /dev/null; then
    echo "Помилка: systemd-socket-proxyd не знайдено. Потрібен systemd >= 246."
    echo "Перевірка: systemctl --version"
    exit 1
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
cp "${APP_DIR}/komerciya-mtruck.socket" /etc/systemd/system/komerciya_mtruck.socket
cp "${APP_DIR}/komerciya-mtruck.service" /etc/systemd/system/komerciya_mtruck.service
cp "${APP_DIR}/komerciya-mtruck-app.service" /etc/systemd/system/komerciya_mtruck_app.service
systemctl daemon-reload

# Увімкнення сокета (запуск за запитом — сервіс стартує тільки при переході по посиланню)
systemctl enable komerciya_mtruck.socket
systemctl start komerciya_mtruck.socket

# Зупинка backend якщо він працював (тепер він запускатиметься on-demand)
systemctl stop komerciya_mtruck.service 2>/dev/null || true
systemctl stop komerciya_mtruck_app.service 2>/dev/null || true

echo "=== Деплой завершено ==="
echo "Режим: on-demand — сервіс запускається тільки при переході по посиланню"
echo "Після 5 хв без активності — автоматично зупиняється"
echo "URL: http://91.239.232.91:5000"
echo "Перевірка сокета: systemctl status komerciya_mtruck.socket"
