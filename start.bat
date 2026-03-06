@echo off
chcp 65001 >nul
echo ============================================================
echo    🚀 ГЕНЕРАТОР PDF КОМЕРЦІЙНИХ ПРОПОЗИЦІЙ
echo ============================================================
echo.

REM Перевіряємо чи існує віртуальне середовище
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Помилка: Віртуальне середовище не знайдено!
    echo.
    echo Створіть віртуальне середовище:
    echo    python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Активуємо віртуальне середовище
echo 📦 Активуємо віртуальне середовище...
call venv\Scripts\activate.bat

REM Перевіряємо чи встановлено Flask
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 📥 Встановлюємо Flask...
    pip install Flask
    echo.
)

REM Перевіряємо чи встановлено Playwright
python -c "from playwright.sync_api import sync_playwright" 2>nul
if errorlevel 1 (
    echo 📥 Встановлюємо Playwright...
    pip install playwright
    echo 📥 Встановлюємо браузери для Playwright...
    playwright install chromium
    echo.
)

REM Запускаємо додаток
echo.
echo ✅ Запускаємо додаток...
echo.
echo 📱 Автоматично відкриваємо браузер...
echo ⏹️  Для зупинки натисніть Ctrl+C
echo.
echo ============================================================
echo.

REM Запускаємо Python скрипт в поточному вікні та відкриваємо браузер через 3 секунди
start /B cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Запускаємо Flask в поточному вікні
python app_simple.py

