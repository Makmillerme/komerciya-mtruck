# Налаштування Nginx для komerciyamtruck.duckdns.org

## 1. Скопіювати конфіг на сервер

```bash
# На сервері (або scp з локальної машини)
sudo cp /root/apps/komerciya-mtruck/deploy/nginx-komerciyamtruck.conf /etc/nginx/sites-available/komerciyamtruck
```

## 2. Увімкнути сайт

```bash
sudo ln -sf /etc/nginx/sites-available/komerciyamtruck /etc/nginx/sites-enabled/
```

## 3. Перевірити та перезавантажити Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 4. Готово

Відкрийте: **http://komerciyamtruck.duckdns.org**

---

## HTTPS (опціонально, через Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d komerciyamtruck.duckdns.org
```

Certbot автоматично оновить конфіг для HTTPS.
