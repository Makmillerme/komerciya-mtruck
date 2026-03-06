# Деплой генератора комерційних пропозицій на сервер

## Режим on-demand

Сервіс **не працює постійно**. Він запускається тільки при переході по посиланню і автоматично зупиняється через 5 хвилин після останнього запиту. Це економить ресурси сервера.

---

## Параметри сервера

- **IP:** 91.239.232.91
- **Hostname:** server2102.server-vps.com
- **Логін:** root
- **Шлях до додатків:** `/root/apps`

---

## Крок 1: Підключення до сервера

```powershell
ssh root@91.239.232.91
```

Введіть пароль при запиті.

---

## Крок 2: Підготовка сервера (один раз)

```bash
# Оновлення пакетів
apt update && apt upgrade -y

# Встановлення Python та залежностей для Playwright
apt install -y python3 python3-venv python3-pip

# Залежності для Chromium (Playwright)
apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
```

---

## Крок 3: Копіювання файлів на сервер

**З локальної машини (PowerShell):**

```powershell
cd D:\Project\mtruck\komerciya_mtruck

# Створення папки на сервері
ssh root@91.239.232.91 "mkdir -p /root/apps/komerciya_mtruck"

# Копіювання файлів (без venv та temp)
scp app_simple.py requirements.txt commercial_proposal_final.html root@91.239.232.91:/root/apps/komerciya_mtruck/
scp -r templates root@91.239.232.91:/root/apps/komerciya_mtruck/
scp -r img root@91.239.232.91:/root/apps/komerciya_mtruck/
scp deploy/komerciya-mtruck.service root@91.239.232.91:/root/apps/komerciya_mtruck/
scp deploy/deploy.sh root@91.239.232.91:/root/apps/komerciya_mtruck/
```

**Важливо:** Переконайтеся, що папка `img` містить:
- `img/logo/M-TRUCK logo iron.png`
- `img/qr/qrcode.webp`

---

## Крок 4: Запуск деплою

```bash
ssh root@91.239.232.91
cd /root/apps/komerciya_mtruck
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматично копіює unit-файли в systemd і налаштовує on-demand режим.

---

## Крок 5: Відкриття порту (якщо є firewall)

```bash
# UFW
ufw allow 5000/tcp
ufw reload

# Або iptables
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## Доступ до додатку

Після успішного деплою:

- **URL:** http://91.239.232.91:5000
- Або: http://server2102.server-vps.com:5000

---

## Корисні команди

| Дія | Команда |
|-----|---------|
| Статус сервісу | `systemctl status komerciya_mtruck` |
| Перезапуск | `systemctl restart komerciya_mtruck` |
| Зупинка | `systemctl stop komerciya_mtruck` |
| Логи | `journalctl -u komerciya_mtruck -f` |

---

## Оновлення після змін у коді

```powershell
# З локальної машини — копіюєте оновлені файли
scp app_simple.py root@91.239.232.91:/root/apps/komerciya_mtruck/
scp -r templates root@91.239.232.91:/root/apps/komerciya_mtruck/

# На сервері — перезапуск
ssh root@91.239.232.91 "systemctl restart komerciya_mtruck"
```

---

## Можливі проблеми

### Playwright: Executable doesn't exist

```bash
cd /root/apps/komerciya_mtruck
source venv/bin/activate
playwright install chromium
```

### Порт 5000 зайнятий

Змініть порт у `komerciya-mtruck.service` (наприклад, на 5001) та у `ExecStart`:

```
--bind 0.0.0.0:5001
```

### Timeout при генерації PDF

Таймаут gunicorn встановлено на 120 секунд. Якщо потрібно більше — змініть `--timeout 120` у service-файлі.
