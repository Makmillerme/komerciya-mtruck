# Скрипт копіювання файлів на сервер (запускати з кореня проекту)
# Використання: .\deploy\copy-to-server.ps1

$SERVER = "root@91.239.232.91"
$REMOTE_DIR = "/root/apps/komerciya_mtruck"

Write-Host "=== Копіювання файлів на сервер ===" -ForegroundColor Cyan

# Створення папки на сервері
ssh $SERVER "mkdir -p $REMOTE_DIR"

# Основні файли
scp app_simple.py requirements.txt commercial_proposal_final.html "${SERVER}:${REMOTE_DIR}/"

# Папки
scp -r templates "${SERVER}:${REMOTE_DIR}/"
scp -r img "${SERVER}:${REMOTE_DIR}/"

# Деплой-скрипти (on-demand)
scp deploy/komerciya-mtruck.socket deploy/komerciya-mtruck.service deploy/komerciya-mtruck-app.service "${SERVER}:${REMOTE_DIR}/"
scp deploy/deploy.sh "${SERVER}:${REMOTE_DIR}/"

Write-Host "`nФайли скопійовано. Далі на сервері виконайте:" -ForegroundColor Green
Write-Host "  ssh $SERVER" -ForegroundColor Yellow
Write-Host "  cd /root/apps/komerciya_mtruck && chmod +x deploy.sh && ./deploy.sh" -ForegroundColor Yellow
