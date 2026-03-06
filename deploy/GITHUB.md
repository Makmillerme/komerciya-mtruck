# Публікація на GitHub

## 1. Створення репозиторію

1. Перейдіть на https://github.com/new
2. **Repository name:** `komerciya-mtruck`
3. **Description:** Генератор PDF комерційних пропозицій M-Truck
4. Оберіть **Public**
5. **НЕ** ставлячи галочку "Add a README" (проєкт уже має файли)
6. Натисніть **Create repository**

## 2. Push через Git (PowerShell)

```powershell
cd D:\Project\mtruck\komerciya_mtruck

# Ініціалізація (якщо ще не зроблено)
git init

# Додавання remote (замініть YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/komerciya-mtruck.git

# Додавання файлів
git add .
git status   # перевірте, що venv, uploads, output не включені

# Перший коміт
git commit -m "Initial commit: генератор PDF комерційних пропозицій"

# Push
git branch -M main
git push -u origin main
```

## 3. GitHub MCP (якщо налаштовано)

Якщо GitHub MCP має валідний токен, можна використати:
- `create_repository` — створити публічний репо
- `push_files` — запушити файли

Переконайтеся, що токен має права `repo` у налаштуваннях MCP.
