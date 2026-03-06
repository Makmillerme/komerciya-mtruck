#!/bin/bash

# Переходимо в директорію скрипта
cd "$(dirname "$0")"

# Примітка: Якщо файл не має прав на виконання, macOS може попросити дозвіл при першому запуску

# Перевіряємо чи існує віртуальне середовище
if [ ! -f "venv/bin/activate" ]; then
    osascript -e 'display dialog "❌ Помилка: Віртуальне середовище не знайдено!\n\nСтворіть віртуальне середовище:\npython3 -m venv venv" buttons {"OK"} default button "OK"' 2>/dev/null || echo "❌ Помилка: Віртуальне середовище не знайдено!"
    exit 1
fi

# Активуємо віртуальне середовище
source venv/bin/activate

# Перевіряємо чи встановлено Flask
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Встановлюємо Flask..."
    pip install Flask
fi

# Перевіряємо чи встановлено Playwright та браузери
if ! python -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "📥 Встановлюємо Playwright..."
    pip install playwright
    echo "📥 Встановлюємо браузери для Playwright..."
    playwright install chromium
fi

# Запускаємо Flask
python app_simple.py &
FLASK_PID=$!

# Чекаємо 3 секунди поки Flask запуститься
sleep 3

# Відкриваємо браузер
open http://localhost:5000 2>/dev/null

# Чекаємо поки Flask процес завершиться
wait $FLASK_PID

